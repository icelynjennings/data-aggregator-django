#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from aggr.models import MediaItem, Music, MediaPerson, UserReview, CriticReview

from django.db.models import Avg

import urllib, urllib2
import re
import argparse
import time
import threading
import HTMLParser

class Command(BaseCommand):

    def handle(self, *args, **options):
		items = MediaItem.objects.all()
		
		for i in items:

			user_score = UserReview.objects.filter(media_item_id=i.id).aggregate(Avg('score'))['score__avg']
			score = CriticReview.objects.filter(media_item_id=i.id).aggregate(Avg('score'))['score__avg']
			
			try:
				user_score = round(user_score,1)
			except:
				pass
				
			try:
				score = round(score,1)
			except:
				pass
				
			
			
			if user_score != None:
				i.user_score = user_score
			else:
				i.user_score = 0
				
			if score != None:
				i.score = score
			else:
				i.score = 0
			
						
			i.save()
