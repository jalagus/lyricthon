import urllib2
import xml.etree.ElementTree as ET
from hyphen import Hyphenator, dict_info
from hyphen.dictools import *
from collections import defaultdict
import random

h_en = Hyphenator('en_US', directory='./')

def get_metaphors(word, top = 10):
	response = urllib2.urlopen('http://ngrams.ucd.ie/metaphor-magnet-acl/q?kw=' + word + '&xml=true')
	xml = response.read()
	root = ET.fromstring(xml)
	metaphors = []
	for child in root:
		metaphors += [ child.find('Text').text.strip().split(':')[1] ]

	return metaphors[:top]

def tokenize(text, split_chars = ['"', ':', '-', ',', '.', '(', ')', '/']):
	for c in split_chars:
		text = text.replace(c, " " + c + " ")
	return map(lambda a: a.lower(), text.split())

def ngrams(l, n):
	di = defaultdict(int)
	dp = {}
	for ngram in [tuple(l[i:i+n]) for (i, value) in enumerate(l[:-(n-1)])]:
		di[ngram] += 1
	for ngram in di.keys():
		if ngram[:n-1] not in dp:
			dp[ngram[:n-1]] = []
		dp[ngram[:n-1]] += [ (ngram[-1], di[ngram]) ]
	return dp

def generate_text_syl(mchain, length, start_word = ''):
	def sum_tuples(l):
		return reduce(lambda a,b: a + b[1], l, 0)

	def find_first_word(word):
		for x in mchain.keys():
			if x[0] == word:
				return x
		return random.choice(mchain.keys())

	def syllables(word):
		return len(h_en.syllables(unicode(word))) + 1

	if length < (len(mchain.keys()[0]) * 2):
		length = len(mchain.keys()[0]) * 2
	start = find_first_word(start_word) if start_word != '' else random.choice(mchain.keys())
	
	text = start

	i = sum([syllables(x) for x in start])
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
		i += syllables(start[-1])
		
	temp = [h_en.syllables(unicode(x)) for x in text]
	print "Final", len([x for sublist in temp for x in sublist])
	return ' '.join([x for sublist in temp for x in sublist])
"""
f = open('corpus/pg158.txt', 'r')
content_text = f.read()
temp = tokenize(content_text)
markov_chain = ngrams(temp, 4)
print generate_text_syl(markov_chain, 20)"""