#!/usr/bin/env python

import nltk
import re
import wikipedia
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


def leaves_new(tree, sentence):
	"""Finds NP (nounphrase) leaf nodes of a chunk tree."""
	for subtree in tree.subtrees(filter = lambda t: t.node=='DATE'):
		if re.search("\s[0-9]{4}\s", " " + subtree.leaves()[0][0] + " ") != None:
			yield {"mod_date": subtree.leaves()[0][0], "text": sentence, "actual_date": subtree.leaves()[0][0]}
		elif re.search("\s[0-9]{4}s", " " + subtree.leaves()[0][0] + " ") != None:          
			yield {"mod_date": subtree.leaves()[0][0].replace("s", ""), "text": sentence, "actual_date": subtree.leaves()[0][0]}
		elif re.search("\s[0-9].*th", " " + subtree.leaves()[0][0]) != None:
			yield {"mod_date": subtree.leaves()[0][0].replace("th", "00"), "text": sentence, "actual_date": subtree.leaves()[0][0]}		
		try:
			if re.search("CE", subtree.leaves()[1][0]) != None:
				yield {"actual_date" :subtree.leaves()[0][0], "text": sentence, "mod_date": subtree.leaves()[0][0]}
			elif re.search("BCE", subtree.leaves()[1][0]) != None:
				yield {"actual_date": "-" + subtree.leaves()[0][0],"text":  sentence, "mod_date": subtree.leaves()[0][0]}
			elif re.search("AD", subtree.leaves()[1][0]) != None:
				yield {"actual_date": subtree.leaves()[0][0], "text": sentence, "mod_date": subtree.leaves()[0][0]}
			elif re.search("BC", subtree.leaves()[1][0]) != None:
				yield {"actual_date": "-" + subtree.leaves()[0][0], "text": sentence, "mod_date": subtree.leaves()[0][0]}
		except IndexError:
			pass

def return_data(data):
	data_list = []
	grammer = r"""DATE: {<CD><NNP|NNS|.>}
	                        {<CD>}
				{<JJ><NN>}
				{<JJ>}"""
	cp = nltk.RegexpParser(grammer)
	for sentence in str(data.content.encode("utf-8")).split("."):
		for sentences in leaves_new(cp.parse(nltk.pos_tag(nltk.word_tokenize(sentence))), sentence):
			data_list.append(sentences)
	new_list = sorted(data_list, key= lambda item: item.get("mod_date"))
	return new_list
