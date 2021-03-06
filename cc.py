import urllib2
import xml.etree.ElementTree as ET
from hyphen import Hyphenator, dict_info
from hyphen.dictools import *
from collections import defaultdict
import random
import re
import math
import text_analysis
import nltk

h_en = Hyphenator('en_US', directory='./')
nouns = []

with open('noun_list.txt', 'r') as f:
	for x in f.read().split():
		nouns += [x]

def create_templates(filename):
	posd = {'NN': '[N]', 'JJ': '[A]'}
	templates = []
	with open(filename, 'r') as f:
		for x in f.readlines():
			pos = nltk.pos_tag( tuple(x.split()) )
			templates += [' '.join([posd[w[1]] if w[1] in posd else w[0] for w in pos])]

	return templates

def is_noun(word):
	if word in nouns:
		return True
	else:
		return False

def templated_generator(template, metaphors_n, metaphors_a):
	sentence = []
	for word in template.split():
		if word == '[A]':
			sentence += [random.choice(metaphors_a)]
		elif word == '[N]':
			sentence += [random.choice(metaphors_n)]
		else:
			sentence += [word]

	return ' '.join(sentence)

def get_metaphors(word, top = 10, sentiment = 'pos'):
	if sentiment == 'pos':
		word = '%2B' + word
	else:
		word = '-' + word

	response = urllib2.urlopen('http://ngrams.ucd.ie/metaphor-magnet-acl/q?kw=' + word + '&xml=true')
	xml = response.read()
	try:
		root = ET.fromstring(xml)
		metaphors_n = []
		metaphors_a = []

		for child in root:
			temp = child.find('Text').text.strip().split(':')
			metaphors_n += [ temp[1] ]
			metaphors_a += [ temp[0] ]

		return metaphors_n[:top], metaphors_a[:top]
	except:
		return []

def tokenize(text, split_chars = [], remove_list = ['_','?', ';', ',', '"', ':', '/', '(', ')', '-',  '.']):
	for c in remove_list:
		text = text.replace(c, ' ') # Replace with space, so if there is some connected words like "word1-word2" they are not joined

	for c in split_chars:
		text = text.replace(c, ' ' + c + ' ')
	return map(lambda a: a.lower(), text.split())

def ngrams(l, n):
	n += 1
	di = defaultdict(int)
	dp = {}
	for ngram in [tuple(l[i:i+n]) for (i, value) in enumerate(l[:-(n-1)])]:
		di[ngram] += 1
	for ngram in di.keys():
		if ngram[:n-1] not in dp:
			dp[ngram[:n-1]] = []
		dp[ngram[:n-1]] += [ (ngram[-1], di[ngram]) ]
	return dp

def generate_sentence(mchain, length = 30, start_word = ''):
	def sum_tuples(l):
		return reduce(lambda a,b: a + b[1], l, 0)

	def find_first_word(word):
		for x in mchain.keys():
			if x[0] == word:
				return x
		return random.choice(mchain.keys())

	start = find_first_word(start_word)
	
	text = start

	for i in xrange(length):
		count = 0
		if start not in mchain:
			start = random.choice(mchain.keys())
		breakpoint = random.randint(1, sum_tuples(mchain[start]))
		last = mchain[start][0]
		for x in mchain[start]:
			count += last[1]
			if breakpoint <= count:
				start = start[1:] + (x[0],)
				break
			last = x
		text += (start[-1], )
	return text

def count_syllables_in_sentence(text):
	def syllable_count(word):
		return len(h_en.syllables(unicode(word))) if len(h_en.syllables(unicode(word))) > 0 else 1
	return sum([syllable_count(x) for x in text.split()])

# Does not guarantee syllable count of "length"
def generate_text_syl(mchain, length, metaphors, start_word = ''):
	def sum_tuples(l):
		return reduce(lambda a,b: a + b[1], l, 0)

	def find_first_word(word):
		for x in mchain.keys():
			if x[0] == word:
				return x
		return random.choice(mchain.keys())

	def syllable_count(word):
		return len(h_en.syllables(unicode(word))) if len(h_en.syllables(unicode(word))) > 0 else 1

	if length < (len(mchain.keys()[0]) * 2):
		length = len(mchain.keys()[0]) * 2
	start = find_first_word(start_word) if start_word != '' else random.choice(mchain.keys())
	
	text = start

	i = sum([syllable_count(x) for x in start])
	while i < length:
		count = 0
		breakpoint = random.randint(1, sum_tuples(mchain[start]))
		last = mchain[start][0]
		for x in mchain[start]:
			count += last[1]
			if breakpoint <= count:
				start = start[1:] + (x[0],)
				break
			last = x
		text += (start[-1], )
		i += syllable_count(start[-1])

	temp = []
	for x in text:
		syl = '-'.join(h_en.syllables(unicode(x)))
		if syl == '':
			syl = x
		temp += [syl]

	return ' '.join(temp), i

def prettify(tuples):
	text = ''.join(str(w) for w in tuples)
	text = text.replace(' i ', ' I ')
	text = text[0].upper() + text[1:]
	text = re.sub('\s\.', '.', text)
	text = re.sub('\s\,', ',', text)
	for i in range(2, len(text)):
		if text[i-2] == '.':
			text = text[:i] + text[i].upper() + text[i+1:]
	return text

def get_hyphenated(text):
	final = []
	for w in text.split():
		if len(w) > 0:
			syl = '-'.join(h_en.syllables(unicode(w)))
			if len(syl) > 0:
				final += [syl]
			else:
				final += [w]
	return ' '.join(final)

def generate_lyrics(markov_chain, syllable_count, metaphors_n, metaphors_a, templates):
	templated_rows = []

	if len(metaphors_a) > 0 and len(metaphors_n) > 0:
		random.shuffle(templates)
		for x in templates:
			s = templated_generator(x, metaphors_n, metaphors_a)
			if count_syllables_in_sentence(s) == syllable_count:
				templated_rows += [(get_hyphenated(s), syllable_count)]

		if len(templated_rows) > 0:
			return random.choice(templated_rows)

	limit = 30
	lyrics = generate_text_syl(markov_chain, syllable_count, metaphors_n)
	while lyrics[1] != syllable_count and limit > 0:
		lyrics = generate_text_syl(markov_chain, syllable_count, metaphors_n)
		limit -= 1

	return lyrics
 