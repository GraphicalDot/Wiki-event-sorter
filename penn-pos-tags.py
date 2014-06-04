#!/usr/bin/env python
import mechanize
import BeautifulSoup


def pos_tags():
	html = mechanize.urlopen("http://www.comp.leeds.ac.uk/ccalas/tagsets/upenn.html")
	soup = BeautifulSoup.BeautifulSoup(html.read()) 
	for tr in soup.find("table").findAll("tr"):
		list = []
		for td in tr.findAll("td"):
			list.append(td.text)
		print list[0].ljust(60), "||",list[1].ljust(60), "||",list[2], '\n'


if __name__ == "__main__":
	pos_tags()
