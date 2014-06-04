#!/usr/bin/env python
import goose
import re
import feedparser
import pymongo
import time
import datetime


class Parsing(object):
	def __init__ (self, url, db, collection):
		self.url = url
		connection = pymongo.Connection()
		collection_string = (connection.%s.%s)%(db, collection)
		self.collection = eval(collection_string)
		self.goose = goose.Goose()

	def __str__(self):
		return "use url, db , and collection name as first, second and third argument torun this file"

	def parsing(self):
		rss = feedparser.parse(self.url)
		return rss

	def goose_text(self, rss_url):
		url_data = self.goose.extract(rss_url)
		return  url_data.cleaned_text

	def in_mongo(self):
		rss_data = self.parsing()
		for news in rss_data.items:
			news["published_date"] = datetime.datetime.fromtimestamp( time.mktime(news.published_parsed))
			news["news"] = self.goose_text(news.link)
			self.collection.insert(news)
			

if __name__ == "__main__"
	scrape(sys.argv[1], sys.argv[2], sys.argv[3])



