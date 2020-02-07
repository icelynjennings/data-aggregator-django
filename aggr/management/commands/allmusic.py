#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.utils.encoding import smart_str
from aggr.models import MediaItem, Music, Critic, MediaPerson, CriticReview

from time import strptime

import urllib, urllib2
import re
import argparse
import time
import threading
import HTMLParser

class am_InfoParser(HTMLParser.HTMLParser):
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)

		self.started = False
		self.recording = 0
		self.image_done = False
		self.review = {}

		self.recorded_info = False
		self.hasAuthor = False

		self.review['author'] = ""
		self.review['name'] = ""
		self.review['company'] = ""
		self.review['critic'] = ""
		self.review['score'] = ""
		self.review['genre'] = ""
		self.review['date'] = ""
		self.review['body'] = ""
		self.review['imgurl'] = ""
		
		self.i = 0

	def reset(self):
		HTMLParser.HTMLParser.reset(self)

		self.started = False
		self.recording = 0
		self.image_done = False
		self.review = {}

		self.recorded_info = False
		self.hasAuthor = False

		self.review['author'] = ""
		self.review['name'] = ""
		self.review['company'] = ""
		self.review['critic'] = ""
		self.review['score'] = ""
		self.review['genre'] = ""
		self.review['date'] = ""
		self.review['body'] = ""
		self.review['imgurl'] = ""
		
		self.i = 0
	
	def clean(self):
	
	
		self.review['genre'] = self.review['genre'].replace('Genre','')
		self.review['date'] = self.review['date'].replace('Release Date','')
		self.review['date'] = self.review['date'].replace(',','')
		
		for i in self.review:
			try:
				self.review[i] = self.review[i].strip()
			except:
				pass
			
		# Split date string
		splitdate = self.review['date'].split(' ')
		
		for d in splitdate:
		
			if d.isdigit():
				if len(d) > 2:
					self.review['year'] = int(d)
				else:
					self.review['day'] = int(d)
			else:
				 self.review['month'] = int(strptime(d,'%B').tm_mon )

		
		del self.review['date']
				
	def handle_starttag(self, tag, attributes):
		if self.started:
			if self.recording:
				#self.review[self.mode] += (self.get_starttag_text())
				self.recording += 1

		if not self.recording:							 
			if tag == 'h1':
				for name, value in attributes:
					if name == 'class' and value == 'album-title':	
						self.mode = "name"
						self.started = True
						self.recording = 1

			if tag == 'h2':
				for name, value in attributes:
					if name == 'class' and value == 'album-artist':			
						self.mode = "author"
						self.started = True
						self.recording = 1
					
			if tag == 'span':
				for name, value in attributes:
					if name == 'itemprop' and value == 'author':			
						self.mode = "critic"
						self.started = True
						self.recording = 1

			if tag == 'div':
				for name, value in attributes:
					if name == 'itemprop' and value == 'ratingValue':
						self.mode = "score"
						self.started = True
						self.recording = 1
						
			if tag == 'div':
				for name, value in attributes:
					if name == 'class' and value == 'genre':
						self.mode = "genre"
						self.started = True
						self.recording = 1
						
			if tag == 'div':
				for name, value in attributes:
					if name == 'class' and value == 'release-date':
						self.mode = "date"
						self.started = True
						self.recording = 1
						
			if tag == 'div':
				for name, value in attributes:
					if name == 'itemprop' and value == 'reviewBody':
						self.mode = "body"
						self.started = True
						self.recording = 1
 
			if tag == 'img':
				for name, value in attributes:
					if name == 'class' and value == 'media-gallery-image' and not self.image_done:
						self.review['imgurl'] = attributes[0][1]
						self.image_done = True

	def handle_endtag(self, tag):
	
		if self.recording:
			self.recording -= 1

		if not self.recording:
			self.started = False
		  
	def handle_data(self, data):
		if self.recording:
			self.review[self.mode] += data

class allmusic_review_Parser(HTMLParser.HTMLParser):
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)

		self.started = False
		self.recording = 0

		self.review = {}

		self.recorded_info = False

		self.review['body'] = ""
		self.review['info'] = ""

		self.re_score = re.compile('(?:score)')

	def reset(self):
		HTMLParser.HTMLParser.reset(self)

		self.started = False
		self.recording = 0

		self.review = {}

		self.recorded_info = False

		self.review['body'] = ""
		self.review['info'] = ""

		self.re_score = re.compile('(?:score)')
		
	def handle_starttag(self, tag, attributes):
		if self.started:
			if self.recording:
				self.review[self.mode] += (self.get_starttag_text())
				self.recording += 1
		
		if tag == 'div':
			for name, value in attributes:
				if name == 'class' and value == 'editorial':
					
					if not self.recording:
						self.mode = "body"
						self.started = True
						self.recording = 1
						self.review[self.mode] += (self.get_starttag_text())
						
				if name == 'class' and value == 'info':
					
					if not self.recording and not self.recorded_info:
						self.mode = "info"
						self.recorded_info = True
						self.started = True
						self.recording = 1
						self.review[self.mode] += (self.get_starttag_text())

	def handle_startendtag(self, tag, attrs):
		if self.recording:
				self.review[self.mode] += (self.get_starttag_text())

	def handle_endtag(self, tag):
	
		if self.recording:
			self.recording -= 1

			self.review[self.mode] += '</' + tag + '>'

		if not self.recording:
			self.started = False
		  
	def handle_data(self, data):
		if self.recording:
			self.review[self.mode] += data

			
class am_newmusic_Parser(HTMLParser.HTMLParser):
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)

		self.started = False
		self.recording = 0

		self.review = {}

		self.recorded_info = False

		self.re_score = re.compile('(?:score)')

	def reset(self):
		HTMLParser.HTMLParser.reset(self)

		self.started = False
		self.recording = 0

		self.review = {}

		self.recorded_info = False

		self.html = ""
		
	def handle_starttag(self, tag, attributes):
		if self.started:
			if self.recording:
				self.html += (self.get_starttag_text())
				self.recording += 1
		
		if tag == 'div':
			for name, value in attributes:
				if name == 'class' and value == 'featured-rows':
					
					if not self.recording:
						self.started = True
						self.recording = 1
						self.html += (self.get_starttag_text())
						
	def handle_startendtag(self, tag, attrs):
		if self.recording:
				self.html += (self.get_starttag_text())

	def handle_endtag(self, tag):
	
		if self.recording:
			self.recording -= 1

			self.html += '</' + tag + '>'

		if not self.recording:
			self.started = False
		  
	def handle_data(self, data):
		if self.recording:
			self.html += data



class Command(BaseCommand):
	def handle(self, *args, **options):
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 
			('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'))
		]
		
		pat_album_url = re.compile("/album/(.*?)\"")

		nm = am_newmusic_Parser()
		ip = am_InfoParser()
		
		i = 1
		url = "http://www.allmusic.com/newreleases"

		f = opener.open(url)

		
		html = f.read()
		
		nm.feed(html)
				
		html = nm.html

		urls = re.findall(pat_album_url,html)
		album_urls = []
		for i in urls:
		  if i not in album_urls:
			album_urls.append(i)

		for u in album_urls:

			g = opener.open("http://www.allmusic.com/album/" + u)

			encoding = g.headers.getparam('charset')
			html_review = g.read().decode(encoding, 'ignore')
			ip.feed(html_review)
			ip.clean()

			if ip.review['score'] == '':
				ip.reset()
				time.sleep(1)
				continue	
				
			# Search for author
			author = MediaPerson.objects.filter(name=ip.review['author'])
			
			if author.exists():
				author = author[0]
			else:
				author = MediaPerson(name=ip.review['author'])
				author.save()
							
			# Search for user's review of item
			album = Music.objects.filter(name=ip.review['name'])
			
			if album.exists():
				print '"{0}" already crawled. Skipping.'.format( smart_str (ip.review['name']) )
				album = album[0]
			else:
				print 'Crawling "{0}"...'.format( smart_str (ip.review['name']) ),
			
				album = Music(name=ip.review['name'],
				image_url = ip.review['imgurl'],
				author=author,
				score=0,
				user_score=0)
				album.MediaItem_save()
				
				print "Done."

			# Search for critic 
			critic = Critic.objects.filter(name='allmusic')
			if critic.exists():
				critic = critic[0]
			else:
				critic = Critic(name='allmusic')
				critic.save()
			
			# Search for critic review
			review = CriticReview.objects.filter(media_item=album,
				min_score=0,
				max_score=10,
				critic=critic,
				score=ip.review['score'])
							
			# Create review
			if review.exists():
				review = review[0]
			else:
				review = CriticReview(media_item=album,
				min_score=0,
				max_score=10,
				critic=critic,
				url="http://www.allmusic.com/album/" + u,
				body=ip.review['body'][0:255],
				score=ip.review['score'].strip())
				
				review.save()

			ip.reset()

			time.sleep(1)