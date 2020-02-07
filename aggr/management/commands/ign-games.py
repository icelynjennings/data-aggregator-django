#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from aggr.models import MediaItem, Game, Critic, MediaPerson, CriticReview

from time import strptime

import urllib, urllib2
import re
import argparse
import time
import threading
import HTMLParser


class ign_review_parser(HTMLParser.HTMLParser):
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		
		self.review = {}
		self.review['author'] = ""
		self.review['body'] = ""
		self.review['genre'] = ""
		self.review['date'] = ""
		self.review['leftcol'] = ""
		self.review['rightcol'] = ""
		
		self.started = False
		self.recording = 0

		self.mode = ""

		self.recorded_info = False

	def reset(self):
		HTMLParser.HTMLParser.reset(self)
		
		self.review = {}
		self.review['author'] = ""
		self.review['body'] = ""
		self.review['genre'] = ""
		self.review['date'] = ""
		self.review['leftcol'] = ""
		self.review['rightcol'] = ""
	
		self.started = False
		self.recording = 0

		self.recorded_info = False
		
	def handle_starttag(self, tag, attributes):
		if self.started:
			if self.recording:
				#self.htmls[self.i] += (self.get_starttag_text())
				self.recording += 1
		
		if tag == 'div':
			for name, value in attributes:
				if name == 'id' and value == 'summary':
					
					if not self.recording:
						self.started = True
						self.recording = 1
						self.mode = "body"				
						
				if name == 'class' and value == 'gameInfo-list leftColumn':
					self.started = True
					self.mode = "leftcol"
					#self.started = True
					self.recording = 1
					
				if name == 'class' and value == 'gameInfo-list':

					self.started = True
					self.mode = "rightcol"
					#self.started = True
					self.recording = 1
																		
									


	def handle_endtag(self, tag):
	
		if self.recording:
			self.recording -= 1

			#self.htmls[self.i] += '</' + tag + '>'

		if not self.recording:
			self.started = False
		  
	def handle_data(self, data):
		if self.recording:
			self.review[self.mode] += data
			
	def clean(self):
		pat_date = re.compile("Release Date: (.*?)\n")
		
		self.review['date'] = pat_date.match(self.review['leftcol'])

		pat_publisher = re.compile("Publisher:(.*\n.*?)\n")
		pat_genre = re.compile("Genre:(.*\n.*?)\n")
		pre_developer = re.compile("Developer:(.*\n.*?)\n")
		
		try:
			self.review['publisher'] = pat_publisher.findall(self.review['rightcol'])[0].strip()
		except:
			pass
			
		try:
			self.review['genre'] = pat_genre.findall(self.review['rightcol'])[0].strip()
		except:
			pass
		
		try:
			self.review['author'] = pre_developer.findall(self.review['rightcol'])[0].strip()
		except:
			pass
		
		
			
		self.review.pop("rightcol", None)
		self.review.pop("leftcol", None)
			
class ign_reviewlist_parser(HTMLParser.HTMLParser):
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		
		self.i = -1
		self.pat_review_url = re.compile ("/games/(.*?)")
		self.reviews = []

		self.started = False
		self.recording = 0
		self.htmls = []

		self.mode = ""

		self.recorded_info = False

	def reset(self):
		HTMLParser.HTMLParser.reset(self)
		self.pat_review_url = re.compile ("/games/(.*?)")
		self.i = -1
		
		self.reviews = []
		self.htmls = []
	
		self.started = False
		self.recording = 0
		
		self.mode = ""

		self.recorded_info = False
		
	def handle_starttag(self, tag, attributes):
		if self.started:
			if self.recording:
				self.htmls[self.i] += (self.get_starttag_text())
				self.recording += 1
		
		if tag == 'div':
			for name, value in attributes:
				if name == 'class' and value == 'clear itemList-item':
					
					if not self.recording:
						self.i += 1		
						self.started = True

						
						
						
						review = {}
						review['name'] = ""
						review['score'] = ""
						review['url'] = ""
						review['imgurl'] = ""
						self.reviews.append(review)
						self.htmls.append("")
						self.htmls[self.i] += (self.get_starttag_text())
						

					
				if name == 'class' and value == 'item-title':
					#if self.started:
					self.mode = "name"
					#self.started = True
					self.recording = 1
					
		if tag == 'span':
			for name, value in attributes:
				if name == 'class' and value == 'scoreBox-score':
					#if self.started:
					self.mode = "score"
					#self.started = True
					self.recording = 1
										
		if tag == 'a':
			if self.started:
				for name, value in attributes:
					if name == 'href' and self.pat_review_url.match(value):
					
						#if self.started:
						self.reviews[self.i]['url'] = attributes[0][1]

						#self.started = True
								
									
	def handle_startendtag(self, tag, attributes):
		if self.started:
			if tag == 'img':
					for name, value in attributes:
						if name == 'class' and value == 'item-boxArt':
							#if self.started:

							self.reviews[self.i]['imgurl'] = attributes[1][1]
							#self.started = True

	def handle_endtag(self, tag):
	
		if self.recording:
			self.recording -= 1

			self.htmls[self.i] += '</' + tag + '>'

		if not self.recording:
			self.started = False
		  
	def handle_data(self, data):
		if self.recording and self.i >= 0:
			self.reviews[self.i][self.mode] += data.strip()



class Command(BaseCommand):

	def handle(self, *args, **options):
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 
			('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'))
		]
		
		

		rl = ign_reviewlist_parser()
		ip = ign_review_parser()
		
		i = 1
		url = "http://uk.ign.com/games/reviews"

		f = opener.open(url)

		
		html = f.read().decode('utf8')
		
		rl.feed(html)
			
		
		reviews = rl.reviews
		
		for review in reviews:

			g = opener.open("http://uk.ign.com/" + review['url'])
		
			encoding = g.headers.getparam('charset')
			html_review = g.read().decode(encoding, 'ignore')
			
			ip.feed(html_review)

			ip.clean()
			
			review.update(ip.review)

			
			if review['score'] == '':
				ip.reset()
				time.sleep(1)
				continue	
				
			# Search for author
			author = MediaPerson.objects.filter(name=review['author'])
			
			if author.exists():
				author = author[0]
			else:
				author = MediaPerson(name=review['author'])
				author.save()
				
			# Search for user's review of item
			item = Game.objects.filter(name=review['name'])
			
			if item.exists():
				print '"{0}" already crawled. Skipping.'.format(review['name'])
				item = item[0]
			else:
				print 'Crawling "{0}"...'.format(review['name']),
			
				item = Game(name=review['name'],
				image_url = review['imgurl'],
				author=author,
				score=0,
				user_score=0)
				item.MediaItem_save()
				
				print "Done."

			# Search for critic 
			critic = Critic.objects.filter(name='IGN')
			if critic.exists():
				critic = critic[0]
			else:
				critic = Critic(name='IGN',url='http://www.ign.com')
				critic.save()
			
			# Search for critic review
			critic_review = CriticReview.objects.filter(media_item=item,
				min_score=0,
				max_score=10,
				score=review['score'])
			
			# Create review
			if critic_review.exists():
				critic_review = critic_review[0]
			else:
				critic_review = CriticReview(media_item=item,
				min_score=0,
				max_score=10,
				critic=critic,
				url= "http://uk.ign.com" + review['url'],
				body=review['body'][0:255],
				score=review['score'].strip())

				
				critic_review.save()

			ip.reset()

			time.sleep(1)