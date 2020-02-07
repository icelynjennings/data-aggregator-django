#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
import unicodedata
import string
import urllib, os
from urlparse import urlparse
from django.db.models.signals import post_save
from django.dispatch import receiver

class Company(models.Model):
	name = models.CharField(max_length=50)
	
	def __str__(self):
		return self.name

class MediaPerson(models.Model):
	name = models.CharField(max_length=50)
	
	def __str__(self):
		return self.name
		
class MediaItem(models.Model):
	subtype = models.CharField(max_length=200, default='music') 
	company = models.ForeignKey(Company, blank = True, null = True)
	author = models.ForeignKey(MediaPerson, blank = True, null = True)
	name = models.CharField(max_length=100)
	url = models.CharField(max_length=100)
	release_date = models.DateField(blank = True, null = True)
	score = models.FloatField()
	user_score = models.FloatField()
	genres = models.CharField(max_length=100, blank = True)
	image_path = models.CharField(max_length=100, null = True, blank = True)
	image_url = models.URLField(null=True, blank=True)
	hits = models.IntegerField(default=0)
			
	def MediaItem_save(self):
		self.subtype = self.__class__.__name__.lower() 
		if self.image_url:

			file_save_dir = 'static/images/mediaitem/'
			filename = self.url + '-' + urlparse(self.image_url).path.split('/')[-1]
			retrieve_url = os.path.join(file_save_dir, filename)
			urllib.urlretrieve(self.image_url, retrieve_url)
			self.image_path = os.path.join(file_save_dir, filename)
			self.image_url = ''
		
		else:
			self.image_path = 'static/images/site/default.png'
			
		punctuations = '''’!()[]{};:'"\,<>./?@#$%^&*_~'''
		no_punct = u""
		for char in smart_str(self.name):
			if char not in punctuations:
				try: 
					no_punct = no_punct + char
				except:
					pass
		
		self.url = no_punct.lower().replace(" ", "-")
		self.save()
	
	def __str__(self):
		return smart_str(self.name)
		
	
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    favorites = models.ManyToManyField(MediaItem, related_name='favoritedby')
		
class Critic(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return str(self.name)

class CriticReview(models.Model):
	media_item = models.ForeignKey(MediaItem, blank = True, null = True)
	body = models.CharField(max_length=255, blank = True, null = True)
	score = models.FloatField()
	min_score = models.FloatField()
	max_score = models.FloatField()
	critic = models.ForeignKey(Critic)
	url = models.CharField(max_length=100, blank = True)

	def __str__(self):
		return smart_str(self.critic.name + " " + self.media_item.name + " " + str(self.score))

class UserReview(models.Model):
	media_item = models.ForeignKey(MediaItem, blank = True, null = True)
	body = models.CharField(max_length=255, blank = True, null = True)
	score = models.IntegerField()
	user = models.ForeignKey(User)

	def __str__(self):
		return smart_str(self.user.username + " " + self.media_item.name + " " + str(self.score))
	
class Console(models.Model):
	name = models.CharField(max_length=50)
	
	def __str__(self):
		return smart_str(self.name)

class Music(MediaItem):

	duration = models.IntegerField(blank = True, null = True)
	
	def __str__(self):
		return smart_str(self.name)
		
class Game(MediaItem):
	platform = models.ManyToManyField(Console, related_name='games')
	def __str__(self):
		return self.name
			
class Movie(MediaItem):
	duration = models.IntegerField(blank = True, null = True)
	starring = models.ManyToManyField(MediaPerson, related_name='movies')
	def __str__(self):
		return self.name
		

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created: 
        profile, new = UserProfile.objects.get_or_create(user=instance)