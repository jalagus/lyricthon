import urllib2
import xml.etree.ElementTree as ET
from hyphen import Hyphenator, dict_info
from hyphen.dictools import *
from collections import defaultdict
import random
import re
import math

h_en = Hyphenator('en_US', directory='./')
nouns = []

with open('noun_list.txt', 'r') as f:
	for x in f.read().split():
		nouns += [x]

def is_noun(word):
	if word in nouns:
		return True
	else:
		return False

def get_metaphors(word, top = 10):
	response = urllib2.urlopen('http://ngrams.ucd.ie/metaphor-magnet-acl/q?kw=' + word + '&xml=true')
	xml = response.read()
	try:
		root = ET.fromstring(xml)
		metaphors = []
		for child in root:
			metaphors += [ child.find('Text').text.strip().split(':')[1] ]

		return metaphors[:top]
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

def generate_n_rhyming_sentences(rhymelist, mchain, n, syllables = -1):
	sentences = []

	rhymes = random.sample(rhymelist, n)

	for r in rhymes:
		line = list(generate_text_syl(markov_chain, syllables, r))
		line.reverse()
		sentences += [ line ]

	return sentences

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

