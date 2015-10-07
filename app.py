import os
from flask import Flask, render_template, send_from_directory, request
import cc

class Error:
	def __init__(self, title, msg):
		self.title = title
		self.msg = msg

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

f = open('corpus/pg158.txt', 'r')
content_text = f.read()
temp = cc.tokenize(content_text)
markov_chain = cc.ngrams(temp, 4)

@app.route('/get_title')
def get_title():
	return 'Fear'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# controllers
@app.route('/', methods=['GET', 'POST'])
def index():
	try:
		if request.method == 'POST':
			song = request.form['song']
			title = request.form['title']

			metaphors=cc.get_metaphors(title)
			lyrics = cc.generate_text_syl(markov_chain, len(song.split()))

			return render_template('index.html', song=song, title=title, lyrics=lyrics)
		else:
			return render_template('index.html')
	except:
		error = Error('Error on generation!', 'Error')
		return render_template('index.html', error=error)

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
