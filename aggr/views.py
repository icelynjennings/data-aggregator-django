from django.shortcuts import render

# Create your views here.

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db import models

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, render_to_response, RequestContext, HttpResponseRedirect, HttpResponse

from .forms import UserForm
from .models import MediaItem, Movie, Game, Music, UserProfile, Critic
from .models import UserReview, CriticReview
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib.auth.hashers import check_password
import os, sys, re, operator, datetime
reload(sys)
sys.setdefaultencoding("utf-8")

from django.shortcuts import get_object_or_404
# REST Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MediaItemSerializer
		
from django.db.models import Avg

from utils import scoretobackground

# API List all Media Items
class MediaItemList(APIView):

	def get(self, request):
		MediaItems = MediaItem.objects.all()
		serializer = MediaItemSerializer(MediaItems, many=True)
		return Response(serializer.data)
		

def home(request):

	topmovies = Movie.objects.order_by('-score')[:10]
	topmusic = Music.objects.order_by('-score')[:10]
	topgames = Game.objects.order_by('-score')[:10]

	
	try:
		movies = topmovies[:8]
		
		for r in movies:
			if r.score == int(r.score):
				r.score = int(r.score)
			r.search_url = r.subtype + '/' + r.url
			r.background = scoretobackground(r.score, size="small", max_score = 10)
		
	except:
		pass
		
	try:
		music = topmusic[:8]
		
		for r in music:
			if r.score == int(r.score):
				r.score = int(r.score)
			r.search_url = r.subtype + '/' + r.url
			r.background = scoretobackground(r.score, size="small", max_score = 10)
			
	except:
		pass
		
	try:
		games = topgames[:8]
		
		for r in games:
			if r.score == int(r.score):
				r.score = int(r.score)
			r.search_url = r.subtype + '/' + r.url
			r.background = scoretobackground(r.score, size="small", max_score = 10)
			
	except:
		pass
		
	context_dict = {'music': music, 'games': games, 'movies': movies}
	
	form = UserForm()
	#context = {"form": form, 'topmovies': topmovies,'topgames': topgames, 'topmusic':topmusic}
	template = "home.html"
	return render(request,template,context_dict)
		
def register(request):
	context = RequestContext(request)
	registered = False
	
	message = ""
	
	form = UserForm()
	context = {"form": form}
	template = "register.html"
	
	if request.method == 'POST':
		form = UserForm(data=request.POST)

		if form.is_valid():
			user = form.save()

			user.set_password(user.password)
			user.save()

			registered = True
			
			message = "Registration was succesful."

		else:
			message = "That username is already in use."

	else:
		form = UserForm()

	return render(request, 'register.html', {'message': message, 'form': form, 'registered': registered})

def profile(request, type, pid, mode = "reviews"):
	itemtype = request.GET.get("type", "")
	title = request.GET.get("title", "")
	body = request.GET.get("body", "")
	min_score = request.GET.get("min_score", 0)
	max_score = request.GET.get("max_score", 10)
	
	message = ""
		
	if itemtype == "":
		itemtype = "movie"
		
	sameuser = False
	if request.user.id == int(pid):
		sameuser = True

	if type == "user":
		user = User.objects.get(id=pid)
		userprofile = UserProfile.objects.get(user__id=pid)
			
		if mode == "favorites":
			resultset = userprofile.favorites.filter(subtype=itemtype, name__icontains=title, score__gte=min_score,score__lte=max_score)
			
			if sameuser and request.method == 'POST':
				itemremoved = request.POST['remove']
				userprofile.favorites.remove(itemremoved)
		elif mode == "edit" and sameuser:
				
				if request.method == 'POST':
					oldpassword = request.POST['oldpassword']
					newusername = request.POST['newusername']
					newpassword = request.POST['newpassword']
										
					if not request.user.username == newusername:
						users = User.objects.all()
						for u in users:
							if u.username == newusername:
								message = "That username is already in use."
								return render(request,"user_profile_edit.html", {'message': message, 'sameuser': sameuser, 'profile': user})
					
					if check_password(oldpassword,request.user.password):
						message = "Account details succesfully changed"
						current_user = request.user
						current_user.set_password(newpassword)
						current_user.username = newusername
						current_user.save()
					else:
						message = "Invalid password."
					
				return render(request,"user_profile_edit.html", {'message': message, 'sameuser': sameuser, 'profile': user})

		else:
			mode = "reviews"
			resultset = UserReview.objects.filter(user=pid, media_item__subtype=itemtype, body__icontains=body,media_item__name__icontains=title, score__gte=min_score,score__lte=max_score)
		
			if sameuser and request.method == 'POST':
				itemremoved = request.POST['remove']
				userprofile.favorites.remove(itemremoved)
				
				removedreview = resultset.get(id = itemremoved)
				removedreview.delete()
		
		for r in resultset:
			if mode == "reviews":
				item = MediaItem.objects.get(id = r.media_item.id)
				r.url = '/' + r.media_item.subtype + '/' + item.url
			else:
				item = MediaItem.objects.get(id = r.id)
				r.url = '/' + r.subtype + '/' + item.url
			r.itemname = item.name
			r.image_path = item.image_path
			r.background = scoretobackground(r.score, size="big", max_score = 10)
			

		template = "user_profile.html"
		return render(request,template, {'profile': user, 'sameuser': sameuser, 'UserReviews': resultset})		
		
	if type == "critic":
		critic = Critic.objects.get(id=pid)
		critic.username = critic.name
		resultset = CriticReview.objects.filter(critic=pid, media_item__subtype=itemtype, body__icontains=body,media_item__name__icontains=title, score__gte=min_score,score__lte=max_score )
				
		for r in resultset:
			item = MediaItem.objects.get(id = r.media_item.id)
			print item.name
			r.itemname = item.name
			r.image_path = item.image_path
			#r.url = item.url
			r.background = scoretobackground(r.score, size="big", max_score = 10)
	
		template = "critic_profile.html"
		return render(request,template, {'profile': critic, 'sameuser': sameuser, 'UserReviews': resultset})	
	
def media_list(request, itemtype):
	title = request.GET.get("title", "")
	author = request.GET.get("author", "")
	genres = request.GET.get("genres", "")
	date_start = request.GET.get("date_start", "")
	date_end = request.GET.get("date_end", "")
	min_score = request.GET.get("min_score", 0)
	max_score = request.GET.get("max_score", 10)
	people = request.GET.get("people", "")
	results = []
						
	if itemtype == 'game':	
		results = Game.objects.all()
	if itemtype == 'film':
		results = Movie.objects.all()
	if itemtype == 'music':
		results = Music.objects.all()
		
	template = "media_list.html"
	results = results.filter(name__icontains=title,author__name__icontains=author,score__gte=min_score,score__lte=max_score)
	
	if genres != "":
		genres = genres.split()
		results = reduce(operator.and_, (results.filter(genres__icontains=g) for g in genres))
		
	if date_start != "" or date_end != "":
	
		try:
			datetime.datetime.strptime(date_start, '%Y-%m-%d')
		except ValueError:
			date_start = "0001-01-01"
			
		try:
			datetime.datetime.strptime(date_end, '%Y-%m-%d')
		except ValueError:
			date_end = datetime.datetime.now().strftime('%Y-%m-%d')
	
		results = results.filter(release_date__range=[date_start, date_end])

		
	
	if people != "":
		people = people.split()
		results = reduce(operator.and_, (results.filter(starring__name__icontains=p) for p in people))

	results = results.distinct()
	#results.filter(genres__icontains=genres)
	
	for r in results:
		if r.score == int(r.score):
			r.score = int(r.score)
		r.search_url = r.subtype + '/' + r.url
		r.background = scoretobackground(r.score, size="small", max_score = 10)
		
		
	context_dict = {'results': results}


	return render(request,template,context_dict)


	
def item_reviews(request, itemtype, name):

	# Get db row of item
	if itemtype == 'game':
		i = Game.objects.get(url=name)
   
	if itemtype == 'movie':
		i = Movie.objects.get(url=name)

	if itemtype == 'music':
		i = Music.objects.get(url=name)
				
	reviews = CriticReview.objects.filter(media_item_id = i.id)

	for r in reviews:
		r.background = scoretobackground(r.score, max_score = r.max_score)
	
	context_dict = {}
	
	context_dict = {'reviews': reviews}

	template = "reviews.html"
	return render(request,template,context_dict)


def item_userreviews(request, itemtype, name):

	# Get db row of item
	if itemtype == 'game':
		i = Game.objects.get(url=name)
   
	if itemtype == 'movie':
		i = Movie.objects.get(url=name)

	if itemtype == 'music':
		i = Music.objects.get(url=name)
				
	reviews = UserReview.objects.filter(media_item_id = i.id)

	for r in reviews:
		r.background = scoretobackground(r.score, max_score = 10)
	
	context_dict = {}
	
	context_dict = {'reviews': reviews}

	template = "userreviews.html"
	return render(request,template,context_dict)
	
		
def user_login(request):
	context = RequestContext(request)
	
	message = ""

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/')
			else:
				message = "This account is inactive."
		else:
			message = "Invalid credentials supplied."

	
	return render_to_response('login.html', {'message': message}, context)
	
	
def media_item(request, itemtype, name):


	starring = []
	# Get db row of item
	if itemtype == 'game':
		i = Game.objects.get(url=name)
   
	if itemtype == 'movie':
		i = Movie.objects.get(url=name)
		starring = i.starring.all()

	if itemtype == 'music':
		i = Music.objects.get(url=name)
			
	i.save()
	
	favbtn = ""
	
	message = ""
	
	favbtn_class = 'btn btn-success'
	favbody = 'Add to favorites'	
	

	
	if request.user.is_authenticated():
		userprofile = UserProfile.objects.get(user__id=request.user.id)
		
		favbtn_class = 'btn btn-success'
		favbody = 'Add to favorites'		
		
		for f in userprofile.favorites.all():
			if f.id == i.id:
				favbtn_class = 'btn btn-danger'
				favbody = 'Remove from favorites'
				break
					
		if request.method == 'POST':
			if request.POST.get("favme") == "1":
				if favbody == 'Remove from favorites':
					userprofile.favorites.remove(i)
					return HttpResponseRedirect('/profile/user/' + str(request.user.id) + '/favorites')	
				if favbody == 'Add to favorites':		
					userprofile.favorites.add(i)
					return HttpResponseRedirect('/profile/user/' + str(request.user.id) + '/favorites')
		
	# Search for user's review of item
	vote = UserReview.objects.filter(user=request.user.id, media_item=i)
	
	# Get user's new review from POST
	if request.method == 'POST' and request.POST:

		if not request.user.is_authenticated():
			return HttpResponseRedirect('/login')	
										   
		user_score = request.POST.get("rate", "")
		user_body = request.POST.get("body", "")	
		
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', user_body)
		if len(urls) > 0:
			return HttpResponseRedirect('/') 
			message = "Spam detected. Did you post a URL?"
			
		if vote.exists():
			for v in vote:
				v.score = int('0' + user_score)
				v.body = user_body
				v.save()
		else:
			curr_user = User.objects.get(id=request.user.id)
			vote = UserReview(user=curr_user,media_item=i,score=user_score,body=user_body)
			vote.save()
			

	i.user_score = UserReview.objects.filter(media_item__id = i.id).aggregate(Avg('score')).values()[0]
	try:
		i.user_score = round(i.user_score,1)
	except:
		pass
		
	if i.user_score == None:
		i.user_score = 0		

	i.save()
					
	context_dict = {}
	context_dict.update({'starring': starring, 'message': message, 'favbody': favbody, 'favbtn_class': favbtn_class})
	
	# Pass current item
	i.critic_background = scoretobackground(i.score, max_score = 10)
	i.user_background = scoretobackground(i.user_score, max_score = 10)
	if i.score == int(i.score):
		i.score = int(i.score)
		
	if i.user_score == int(i.user_score):
		i.user_score = int(i.user_score)
		
	context_dict.update({'object': i})
				
	# Pass 5 critic reviews
	cr = CriticReview.objects.filter(media_item_id=i.id).order_by('-id')[:5]
	critic_reviews = []
	for x in cr:
		if x.score == int(x.score):
			x.score = int(x.score)
		critic_reviews.append(x)
		x.criticid = x.critic.id
		y = critic_reviews[-1]
		
		y.background = scoretobackground(y.score, max_score= y.max_score)
		print y.background
	context_dict.update({'CriticReviews': critic_reviews})
		
	# Pass 5 user reviews
	ur = UserReview.objects.filter(media_item_id=i.id).order_by('-id')[:5]
	user_reviews = []
	for x in ur:
		user_reviews.append(x)
		y = user_reviews[-1]
		
		y.background = scoretobackground(y.score, max_score = 10)
		print y.background
	context_dict.update({'UserReviews': user_reviews})
	
	# Render
	return render_to_response("media_item.html",
							  context_dict,
							  context_instance=RequestContext(request))
			
			   
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/')