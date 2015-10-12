from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

analyzer = NaiveBayesAnalyzer()

def has_positive_sentiment(text):
	analysis = TextBlob(text, analyzer=analyzer)
	if analysis.sentiment.classification == 'pos':
		return True
	return False
