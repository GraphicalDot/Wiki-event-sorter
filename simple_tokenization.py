#!/usr/bin/env python
import nltk
import re
import wikipedia
from flask import Flask
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from flask import jsonify
import wikiapi
app = Flask(__name__)
"""
This py files uses the nltk mocule along with punkt sentence tokenizer and maxent word tokenizer to parse the given string on the basis
of regex supplied to it
"""

def tokenizer(doc):
	sentences = nltk.sent_tokenize(doc)
	sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	grammar = "NP: {<CD><NNP|NNS|.>}"
	cp = nltk.RegexpParser(grammar)
	print [cp.parse(sentence) for sentence in sentences]

class Finding_Dates:
	def __init__(self, doc):
		self.doc = doc

	def tokenization_date(self):
		sentence = nltk.sent_tokenize(self.doc)
		sentences = [nltk.word_tokenize(sentence) for sentence in sentence]
		sentences = [nltk.pos_tag(sent) for sent in sentences]
		grammar = r"""DATE: {<CD><NNP|NNS|.>}
			    {<JJ><NN>}
			    {<JJ>}
			    {<CD>}"""

		cp = nltk.RegexpParser(grammar)
		return [(cp.parse(sentence), sentence) for sentence in sentences]

	def leaves(self, tree, sentence):
		"""Finds phrase leaf nodes of a chunk tree."""
		for subtree in tree.subtrees(filter = lambda t: t.node== "DATE"):
			if re.match("[0-9]\w+", subtree.leaves()[0][0]) != None:
				yield (subtree.leaves(), sentence)

	def print_filtered_dates(self):
		for tree, sentence in self.tokenization_date():
			for filtered_nodes in self.leaves(tree, sentence):
				print filtered_nodes


def scrape(url):                                   
	br = mechanize.Browser()
	br.set_handle_equiv(True)
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	r = br.open(url)
	return r.read()

#This is a function to remove [] in wikipedia articles if any
def removing_brackets(string):
	for item in string.split("."):
		print " ".join(map(lambda x: "" if re.match("\[\d+\]", x) != None else x, item.split(" ")))



def leaves_old(tree, sentence):
	for subtree in tree.subtrees(filter = lambda t: t.node=='DATE'):
		if re.search("[0-9]\w+", subtree.leaves()[0][0]) != None:
			yield (sentence, subtree.leaves())



def leaves_new(tree, sentence):
	"""Finds NP (nounphrase) leaf nodes of a chunk tree."""
	for subtree in tree.subtrees(filter = lambda t: t.node=='DATE'):
		if re.search("\s[0-9]{4}\s", " " + subtree.leaves()[0][0] + " ") != None:
			yield {"mod_date": subtree.leaves()[0][0], "text": sentence, "actual_date": subtree.leaves()[0][0]}
		elif re.search("\s[0-9]{4}s", " " + subtree.leaves()[0][0] + " ") != None:          
			yield {"mod_date": subtree.leaves()[0][0].replace("s", ""), "text": sentence, "actual_date": subtree.leaves()[0][0]}
#		elif re.search("\s[0-9].*th", " " + subtree.leaves()[0][0]) != None:
#			yield {"mod_date": subtree.leaves()[0][0].replace("th", "00"), "text": sentence, "actual_date": subtree.leaves()[0][0]}		
		try:
			if re.search("CE", subtree.leaves()[1][0]) != None:
				yield {"actual_date" :subtree.leaves()[0][0], "text": sentence, "mod_date": subtree.leaves()[0][0]}
			elif re.search("BCE", subtree.leaves()[1][0]) != None:
				yield {"actual_date": "-" + subtree.leaves()[0][0],"text":  sentence, "mod_date": subtree.leaves()[0][0]}
			elif re.search("AD", subtree.leaves()[1][0]) != None:
				yield {"actual_date": subtree.leaves()[0][0], "text": sentence, "mod_date": subtree.leaves()[0][0]}
			elif re.search("BC", subtree.leaves()[1][0]) != None:
				yield {"actual_date": "-" + subtree.leaves()[0][0], "text": sentence, "mod_date": subtree.leaves()[0][0]}
			elif re.search("[cC]entury", " " + subtree.leaves()[1][0]) != None:
				yield {"mod_date": subtree.leaves()[0][0].replace("th", "00"), "text": sentence, "actual_date": subtree.leaves()[0][0]}		
		except IndexError:
			pass

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods
		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp

			h = resp.headers

			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp

		f.provide_automatic_options = False
		return update_wrapper(wrapped_function, f)
	return decorator

def return_data(data):
	data_list = []
	#grammer = r"""DATE: {<CD><NNP|NNS|.>}
	 #                       {<CD>}
	#			{<JJ><NN>}
	#			{<JJ>}"""
	grammer = r"""DATE: {<CD><NNP|NNS|.>}
                              {<CD><.|,>}
                              {<IN><DT><JJ><NN>}
                              {<JJ>}                                                                           
                     {<IN><CD>}"""
	cp = nltk.RegexpParser(grammer)
	sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

#	for sentence in nltk.tokenize.sent_tokenize(data.content.encode("utf-8")):
	for sentence in sent_tokenizer.tokenize(data.content.encode("utf-8")):
		for sentences in leaves_new(cp.parse(nltk.pos_tag(nltk.word_tokenize(sentence))), sentence):
			data_list.append(sentences)
	new_list = sorted(data_list, key= lambda item: item.get("mod_date"))
	seen, result =set(), []
	for item in new_list:
		if item.get("text") not in seen:
			result.append(item)
			seen.add(item.get("text"))
#	return (result, data.content.encode("utf-8").split("\n\n\n")[0])
	return (result, data.summary)


@app.route('/search', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def SampleResource():
	args = request.args.get('query')
	try:
		wiki = wikiapi.WikiApi()
		results = wiki.find(args)
		article = wiki.get_article(results[0])
                data = return_data(article)
		return jsonify({"data": data[0],
			"data_head": {"data_tag": data[1], "image_src": article.image},
                        "error": False,
                        "success": True,})
        except wikipedia.DisambiguationError as e:
		return jsonify({"data": e.__str__(), "error": True})

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug= True)
