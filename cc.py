import urllib2
import xml.etree.ElementTree as ET

def get_metaphors(word, top = 5):
	response = urllib2.urlopen('http://ngrams.ucd.ie/metaphor-magnet-acl/q?kw=' + word + '&xml=true')
	xml = response.read()
	root = ET.fromstring(xml)
	metaphors = []
	for child in root:
		metaphors += [ child.find('Text').text.strip().split(':')[1] ]

	return metaphors[:top]