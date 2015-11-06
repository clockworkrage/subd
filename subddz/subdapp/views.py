# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from subdapp.models import User, Forum, Thread, Post
import logging
import json
from django.db import connection
from django.db.models.fields.related import ManyToManyField
from django.core import serializers

logger = logging.getLogger(__name__)

def to_dict(instance):
	opts = instance._meta
	data = {}
	for f in opts.concrete_fields + opts.many_to_many:
		if isinstance(f, ManyToManyField):
			if instance.pk is None:
				data[f.name] = []
			else:
				data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
		else:
			data[f.name] = f.value_from_object(instance)
	return data

def index(request):
	
	response = JsonResponse({'foo': 'bar'})
	return response

def user_create(request):

	main_response = {}
	
	if request.method == 'POST':
	#for key in request.GET:
		#logger.error(r"ssss")
		input_params = json.loads(request.body)
		#logger.error(req["name"])
		#logger.error(request.FILES)
		#logger.error(request.body)

		isUserExistsError = False
		json_response = {}

		isAnon = input_params['isAnonymous']
		email = input_params['email']

		if isAnon:
			about = "Null"
			name = "Null"
			username = "Null"
		else:
			about = input_params['about']
			name = input_params['name']
			username = input_params['username']

		user_id = 0
		num_results = User.objects.filter(email = email).count()

		if num_results != 0:
			isUserExistsError = True

		if isUserExistsError == False:
			user = User(name=name, username=username, isAnonymous=isAnon, email=email, about=about)
			user.save()
			user_id = user.id

			main_response = {'code':0}
			json_response['about'] = about
			json_response['email'] = email
			json_response['id'] = user_id
			json_response['isAnonymous'] = isAnon
			json_response['name'] = name
			json_response['username'] = username

		if isUserExistsError == True:
			main_response = {'code':5}
			json_response = "error message"


	

	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

def clear(request):
	cursor = connection.cursor()

	cursor.execute("DELETE FROM subdapp_forum")
	connection.commit()
	cursor.execute("DELETE FROM subdapp_user_follow")
	connection.commit()

	cursor.execute("DELETE FROM subdapp_thread_subscribe")
	connection.commit()
	
	cursor.execute("DELETE FROM subdapp_user;")
	connection.commit()

	cursor.execute("DELETE FROM subdapp_forum") 
	connection.commit()

	cursor.execute("DELETE FROM subdapp_thread")
	connection.commit()

	cursor.execute("DELETE FROM subdapp_post")
	connection.commit()
	

	main_responce = {'code':0}
	main_responce['response'] = "OK"

	response = JsonResponse(main_responce)
	return response

def get_user_info(user_detail):
	info = {}

	if user_detail.isAnonymous == False:
		info['about'] = user_detail.about
		info['username'] = user_detail.username
		info['name'] = user_detail.name
		info['followers'] = list(User.objects.values_list('email', flat=True).filter(follow=user_detail))
		info['following'] = list(user_detail.follow.values_list('email', flat=True).filter())
	else:
		info['about'] = None
		info['username'] = None
		info['name'] = None
		info['followers'] = []
		info['following'] = []

	info['subscriptions'] = list(Thread.objects.values_list('id', flat=True).filter(subscribe=user_detail))

	info['id'] = user_detail.id
	info['isAnonymous'] = user_detail.isAnonymous
	info['email'] = user_detail.email
	
	
	return info

#Requesting http://some.host.ru/db/api/user/details/?user=example%40mail.ru:	
def user_details(request):

	main_response = {'code':0}

	json_response = {}

	user_email = request.GET['user']

	user_detail = User.objects.get(email = user_email)
	
	main_response['response'] = get_user_info(user_detail)

	response = JsonResponse(main_response)
	return response

def user_follow(request):

	main_response = {}
	json_response = {}

	if request.method == 'POST':
	#for key in request.GET:
		#logger.error(r"ssss")
		input_params = json.loads(request.body)

		follower_email = input_params['follower']
		followee_email = input_params['followee']
		json_response = {}

		
		follower_user = User.objects.get(email = follower_email)
		followee_user = User.objects.get(email = followee_email)

		#logger.error(follower_user)
		#logger.error(followee_user)

		follower_user.follow.add(followee_user)

		main_response = {'code':0}

		json_response = get_user_info(follower_user)

	

	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

def user_updateProfile(request):

	main_response = {'code':0}

	json_response = {}

	if request.method == 'POST':
		input_params = json.loads(request.body)

		about = input_params['about']
		user_email = input_params['user']
		user_name = input_params['name']

	response = JsonResponse(main_response)
	return response

def dictfetchall(cursor):

	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]

def status(request):

	cursor = connection.cursor()

	cursor.execute("Select USR.user_number, FORM.forum_number, THR.thread_number, PST.post_number FROM \
		 (Select COUNT(*) user_number from subdapp_user) USR, \
		 (Select COUNT(*) forum_number from subdapp_forum) FORM, \
		 (Select COUNT(*) thread_number from subdapp_thread) THR, \
		 (Select COUNT(*) post_number from subdapp_post) PST;")

	row = dictfetchall(cursor)
	
	json_response = {}
	json_response['user'] = str(row[0]['user_number'])
	json_response['thread'] = str(row[0]['forum_number'])
	json_response['forum'] = str(row[0]['thread_number'])
	json_response['post'] = str(row[0]['post_number'])

	main_response = {'code':0}
	
	main_response['response'] = json_response;
	response = JsonResponse(main_response)
	return response

#Requesting http://some.host.ru/db/api/forum/create/ with {"name": "Forum With Sufficiently Large Name", "short_name": "forumwithsufficientlylargename", "user": "richard.nixon@example.com"}:
def forum_create(request):

	main_response = {'code':0}
	
	if request.method == 'POST':
		input_params = json.loads(request.body)
		#logger.error("user_email")
		#logger.error(request.body)

		name = input_params['name']
		short_name = input_params['short_name']
		user_email = input_params['user']
		

		#logger.error("user_email22")
		#logger.error(name)
		user = User.objects.get(email = user_email)
		#logger.error(user)
		forum = Forum(name=name, short_name=short_name, user=user)
		forum.save()

		json_response = {}
		json_response['id'] = forum.id
		json_response['name'] = forum.name
		json_response['short_name'] = forum.short_name
		json_response['user'] = user.email

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response
#http://some.host.ru/db/api/forum/details/?related=user&forum=forum3:
def forum_details(request):
	main_response = {}
	json_response = {}
	if request.method == 'GET':
		short_name = request.GET['forum']
		related = request.GET['related']

		forum = Forum.objects.get(short_name = short_name)

		main_response = {'code':0}
		json_response['id'] = forum.id
		json_response['name'] = forum.name
		json_response['short_name'] = forum.short_name

		if related.count('user') == 1:
			json_response['user'] = get_user_info(forum.user)


	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response

def post_create(request):
	#logger.error("POST:")
	main_response = {'code':0}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		#logger.error("user_email")
		#logger.error(request.body)

		isApproved = input_params['isApproved']
		user_email = input_params['user']
		date = input_params['date']
		message = input_params['message']
		isSpam = input_params['isSpam']
		isHighlighted = input_params['isHighlighted']
		thread_id = input_params['thread']
		forum_name = input_params['forum']
		isDeleted = input_params['isDeleted']
		isEdited = input_params['isEdited']

		

		
		#logger.error(name)
		user = User.objects.get(email = user_email)
		#logger.error("GET1")
		thread = Thread.objects.get(id = thread_id)
		#logger.error("GET2")
		forum = Forum.objects.get(short_name = forum_name)
		#logger.error("GET3")
		post = Post(date = date, user = user, thread = thread, forum = forum, isApproved = isApproved, isHighlighted = isHighlighted, 
			isEdited = isEdited, isSpam = isSpam, isDeleted = isDeleted, message = message, parent = 0)
		post.save()

		#logger.error("CREATED")
		
		json_response['id'] = post.id
		json_response['date'] = post.date
		json_response['forum'] = forum.short_name
		json_response['isApproved'] = post.isApproved
		json_response['isDeleted'] = post.isDeleted
		json_response['isEdited'] = post.isEdited
		json_response['isHighlighted'] = post.isHighlighted
		json_response['isSpam'] = post.isSpam
		json_response['message'] = post.message
		json_response['parent'] = post.parent
		json_response['thread'] = thread.id
		json_response['user'] = user.email


	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

# Requesting http://some.host.ru/db/api/thread/create/ with
#  {"forum": "forum1", "title": "Thread With Sufficiently Large Title", 
#  "isClosed": true, "user": "example3@mail.ru", "date": "2014-01-01 00:00:01",
#   "message": "hey hey hey hey!", "slug": "Threadwithsufficientlylargetitle", "isDeleted": true}:
def thread_create(request):
	#logger.error("THREAD:")
	main_response = {'code':0}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		
		
		#logger.error(request.body)
		
		forum_name = input_params['forum']
		title = input_params['title']
		isClosed = input_params['isClosed']
		user_email = input_params['user']
		date = input_params['date']
		message = input_params['message']
		slug = input_params['slug']	
		isDeleted = input_params['isDeleted']

		

		#logger.error("DONE")
		#logger.error(name)
		#try:
		user = User.objects.get(email = user_email)
		forum = Forum.objects.get(short_name = forum_name)

		thread = Thread (date = date, user =user, forum = forum, title = title, slug = slug, message = message,
			isClosed = isClosed, isDeleted = isDeleted)
		thread.save()

		json_response['id'] = thread.id
		json_response['date'] = thread.date
		json_response['forum'] = forum.short_name
		json_response['isClosed'] = thread.isClosed
		json_response['isDeleted'] = thread.isDeleted
		json_response['message'] = thread.message
		json_response['title'] = thread.title
		json_response['user'] = user_email
		#logger.error("THREAD CREATED")


	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response