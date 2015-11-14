# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from subdapp.models import User, Forum, Thread, Post
import logging
import json
from django.db import connection
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.utils import dateformat
from django.conf import settings

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
	#logger.error("Update")
	main_response = {}
	json_response = {}

	if request.method == 'POST':
		input_params = json.loads(request.body)

		about 		= input_params['about']
		user_email 	= input_params['user']
		user_name 	= input_params['name']
		#logger.error("READED")
		user = User.objects.get(email = user_email) #.update(about = about, user_name = user_name)
		user.about = about
		user.name = user_name
		user.save(update_fields=['about', 'name'])
		#logger.error(user)
		main_response = {'code':0}
		json_response = get_user_info(user)

	main_response['response'] = json_response;
	response = JsonResponse(main_response)
	return response


	#Requesting http://some.host.ru/db/api/user/listFollowers/?user=example%40mail.ru&order=asc:
def user_listFollowers(request):
	#logger.error("user_listFollowers")
	main_response = {}
	json_response = {}
	if request.method == 'GET':

		user_email = request.GET['user']
		order = request.GET['order']
		limit = request.GET.get('limit', 0)
		offset = request.GET.get('since_id', 0)

		#logger.error("reeaded")
		user = User.objects.get(email = user_email)

		if order == 'desc':
			sort_order = '-name'
		else:
			sort_order = 'name'

		followers_list = []

		if (limit != 0) and (offset != 0):
			followers_list = list(User.objects.values_list('email', flat=True).filter(follow=user).order_by(sort_order)[offset:limit + offset])
		else:
			followers_list = list(User.objects.values_list('email', flat=True).filter(follow=user).order_by(sort_order))
		
		out_list = []

		for follower in followers_list:
			follow_user = User.objects.get(email = follower)
			out_list.append(get_user_info(follow_user))

		main_response = {'code':0}
		json_response = out_list
		
	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response