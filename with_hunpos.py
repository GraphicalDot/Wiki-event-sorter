#!/usr/bin/env python
# -*- coding: utf-8 -*-
import nltk
import re
import wikipedia
from flask import Flask
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from flask import jsonify
import wikiapi
import time
app = Flask(__name__)
"""
This py files uses the nltk mocule along with punkt sentence tokenizer and maxent word tokenizer to parse the given string on the basis
of regex supplied to it
"""


def leaves_new(tree, sentence):
	"""Finds NP (nounphrase) leaf nodes of a chunk tree."""
	for subtree in tree.subtrees(filter = lambda t: t.node=='DATE'):
		if re.search("\s[0-9]{4}\s", " " + subtree.leaves()[0][0] + " ") != None:
			print subtree.leaves(), sentence
			yield {"mod_date": subtree.leaves()[0][0], "text": sentence, "actual_date": subtree.leaves()[0][0]}
		elif re.search("\s[0-9]{4}s", " " + subtree.leaves()[0][0] + " ") != None:          
			print subtree.leaves(), sentence
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
	grammer = r"""DATE: {<CD><NNP|NNS|.>}
                              {<CD><.|,>}
                              {<IN><DT><JJ><NN>}
                              {<JJ>}                                                                           
                     {<IN><CD>} 
		"""
		
	new_grammer = r"""DATE: {<NNP><JJ><NN>}
				{<NNP><CD><CD>}
				{<CD><NNP><NNS>}
				{<JJ>}
				{<IN><NNP><CD>}
				{<NNP><CD><NN>}
				{<IN><CD>} 
				{<VBD>}
				{<NNP><VBZ><VBG>}
				{<IN><VBG>}
				{<CD><NNP>}
				{<JJ><NN>}
				{<CD><NNS>}
				{<IN><RB>}
				"""

	cp = nltk.RegexpParser(grammer)
	sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	ht = nltk.HunposTagger(path_to_model='/usr/local/bin/en_wsj.model', path_to_bin='/usr/local/bin/trunk/tagger.native')

	for sentence in sent_tokenizer.tokenize(data.content.encode("utf-8")):
		for sentences in leaves_new(cp.parse(ht.tag(nltk.word_tokenize(sentence))), sentence):
			data_list.append(sentences)
	ht.close()
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
	epoch = time.time()
	args = request.args.get('query')
	try:
		wiki = wikiapi.WikiApi()
		results = wiki.find(args)
		article = wiki.get_article(results[0])
                data = return_data(article)
		print time.time() - epoch
		return jsonify({"data": data[0],
			"data_head": {"data_tag": data[1], "image_src": article.image},
                        "error": False,
                        "success": True,})
        except wikipedia.DisambiguationError as e:
		return jsonify({"data": e.__str__(), "error": True})

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug= True)


	"""
	<JJ><NN>} "in late 2011.
			"check with NN"
	{<NNP><CD><CD>}
	{<CD><NNP><NNS>} "Negative from Stable on 18 June 2012."
		"NNS with four digits"
	{<JJ>} "In the 6th and", "and 7th centuries, the first"
	{<IN><NNP><CD>}
	{<NNP><CD><NN>}
	{<IN><CD>} "between 1848 and 1885","off the Indian Rebellion of 1857.", "in 1206.", " clocked at 800 MHz."
			"Check for the CD with four digits"
	{<VBD>}
		"As of September 2012,"
	{<NNP><VBZ><VBG>}
		"By October 12, 2011, the"
			"Check for VBG four digit number"
	{<IN><VBG>} "was suppressed by 1858,"
			"Check for the VBG with four digits"
	
	{<CD><NNP>} "During the Vedic period (c. 1700–500 BCE),"During the period 2000–500 BCE,", 
		    "between 200 BCE and 200 CE, "medieval age, 600 CE to 1200 CE, is", 
			"Check for the cd with four digits"
	
	{<JJ><NN><NNP>} "In the late Vedic period, around the 5th century BCE,"10th century, Muslim"
			"Check for the \d*th"
	
	{<CD><NNS>} "about 30,000 years ago", "According to a 2011 PricewaterhouseCoopers report,"
			"Check for the <CD> with more than four numbers"
	{<IN><RB>} "grew by 15.1% in 2012-13, increasing"
			"check for number in RB"
	"""

