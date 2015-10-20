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
			about = "about"
			name = "name"
			username = "username"
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

			main_response = {'code':'0'}
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
	#cursor.execute("DELETE FROM subdapp_thread_subscribe")
	cursor.execute("DELETE FROM subdapp_user;")
	connection.commit()
	#cursor.execute("DELETE FROM subdapp_forum") 
	#cursor.execute("DELETE FROM subdapp_thread")
	#cursor.execute("DELETE FROM subdapp_post")
	
	

	main_responce = {'code':'0'}
	main_responce['response'] = "OK"

	response = JsonResponse(main_responce)
	return response

def get_user_info(user_detail):
	info = {}
	info['about'] = user_detail.about
	info['email'] = user_detail.email
	
	info['followers'] = list(User.objects.values_list('email', flat=True).filter(follow=user_detail))
	info['following'] = list(user_detail.follow.values_list('email', flat=True).filter())

	info['subscriptions'] = list(Thread.objects.values_list('id', flat=True).filter(subscribe=user_detail))

	info['id'] = user_detail.id
	info['isAnonymous'] = user_detail.isAnonymous
	info['name'] = user_detail.name
	info['username'] = user_detail.username
	return info

#Requesting http://some.host.ru/db/api/user/details/?user=example%40mail.ru:	
def user_details(request):

	main_response = {'code':'0'}
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

		logger.error(follower_user)
		logger.error(followee_user)

		follower_user.follow.add(followee_user)

		main_response = {'code':'0'}

		json_response = get_user_info(follower_user)

	

	main_response['response'] = json_response;
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

	main_response = {'code':'0'}
	
	main_response['response'] = json_response;
	response = JsonResponse(main_response)
	return response

#Requesting http://some.host.ru/db/api/forum/create/ with {"name": "Forum With Sufficiently Large Name", "short_name": "forumwithsufficientlylargename", "user": "richard.nixon@example.com"}:
def forum_create(request):

	main_response = {'code':'0'}
	
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