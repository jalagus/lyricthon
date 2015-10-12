import os
from flask import Flask, render_template, send_from_directory, request
import cc
import lilypond
import random
import text_analysis

NGRAM_SIZE = 3
PORT = 5000

current_version = 1

templates = cc.create_templates('templates.txt')

class Error:
	def __init__(self, title, msg):
		self.title = title
		self.msg = msg

# initialization
app = Flask(__name__, static_folder='static')
app.config.update(
    DEBUG = True,
)

f = open('corpus/pg158.txt', 'r')
content_text = f.read()
temp = cc.tokenize(content_text)
markov_chain = cc.ngrams(temp, NGRAM_SIZE)

def generate_title():
	i = 0
	while i < 100:
		i += 1
		title = ' '.join(cc.generate_sentence(markov_chain, 3)).split()
		for j,e in enumerate(title):
			if cc.is_noun(title[j]):
				i = 1000
				break
	return ' '.join(title[:j+1])

@app.route('/get_title')
def get_title():
	return cc.prettify(generate_title())

# Adjust parameters with respect to rating
@app.route('/rate/<int:rating>', methods=['POST'])
def rating(rating):
	data = request.form['lyrics']
	new_chain = cc.ngrams(data.split(), NGRAM_SIZE)
	for key in new_chain:
		if key in markov_chain:
			for new_item in new_chain[key]:
				for index,item in enumerate(markov_chain[key]):
					if item[0] == new_item[0]:
						if item[1] + rating > 0:
							markov_chain[key][index] = (item[0], item[1] + rating)
		else:
			markov_chain[key] = new_chain[key]
	return str(rating)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# controllers
@app.route('/', methods=['GET', 'POST'])
def index():
	global current_version
	song = ""
	title = ""
	try:	
		if request.method == 'POST':
			song = request.form['song'] if request.form['song'] else ''
			title = request.form['title'] if request.form['title'] else ''	

			sentiment = 'neg'
			if text_analysis.has_positive_sentiment(title):
				sentiment = 'pos'

			# Get metaphors to be used in generation
			metaphors_n = []
			metaphors_a = []
			for x in title.split():
				m = cc.get_metaphors(x, 30, sentiment)
				if len(m) > 1:
					metaphors_n += m[0]
					metaphors_a += m[1]

			final = ''
			final_list = []
			for verse in song.split('\n'):
				sv = [x for x in verse.split() if 'r' not in x]

				lyrics = cc.generate_lyrics(markov_chain, len(sv), metaphors_n, metaphors_a, templates)

				final_list += [lyrics[0].replace('-', '')]
				final += cc.prettify(lyrics[0] + '.\n\n')

			current_version += 1
			lilypond.generate_pdf(song, final, title)

			return render_template('index.html', song=song, title=title, lyrics=final, lyricdata=' '.join(final_list), version=current_version)
		else:
			return render_template('index.html', song=song, title=title)
	except Exception, e:
		print e
		error = Error('Error on generation!', 'Error')
		return render_template('index.html', error=error, song=song, title=title)

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", PORT))
    app.run(host='0.0.0.0', port=port)
