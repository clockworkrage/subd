# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from subdapp.models import User, Forum, Thread, Post, User_Post_Forum
import json
import logging
from django.db import connection
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.utils import dateformat
from django.conf import settings
from utils import check_dict

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

def find_list(search_list, value):

	for element in search_list:
		if element == value:
			return True;

	return False

def user_create(request):

	main_response = {}
	
	if request.method == 'POST':

		input_params = json.loads(request.body)

		required = ['username', 'about', 'name', 'email']

		try:
			check_dict(input_params, required)
		except Exception as e:
			if e.message == 'required':
				return JsonResponse({'code':1, 'response': e.message})

		isUserExistsError = False
		json_response = {}

		isAnon = input_params['isAnonymous']
		email = input_params['email']

		if isAnon:
			about = ''
			name = ''
			username = ''
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

def get_post_info(post_details, related):

	info = {}

	info['date']			= dateformat.format(post_details.date, settings.DATETIME_FORMAT)
	info['dislikes']		= post_details.dislikes

	if find_list(related, 'forum'):
		info['forum']	= get_forum_info(post_details.forum)
	else:
		info['forum']	= post_details.forum.short_name

	info['id']				= post_details.id
	info['isApproved']		= post_details.isApproved
	info['isDeleted']		= post_details.isDeleted
	info['isEdited']		= post_details.isEdited
	info['isHighlighted']	= post_details.isHighlighted
	info['isSpam']			= post_details.isSpam
	info['likes']			= post_details.likes
	info['message']			= post_details.message
	if post_details.parent != 0:
		info['parent']		= post_details.parent
	info['points']			= post_details.points

	if find_list(related, 'thread'):
		info['thread']	= get_thread_info(post_details.thread, [])
	else:
		info['thread']	= post_details.thread.id

	if find_list(related, 'user'):
		info['user']	= get_user_info(post_details.user)
	else:
		info['user']	= post_details.user.email



	return info

#Requesting http://some.host.ru/db/api/user/details/?user=example%40mail.ru:	
def user_details(request):
	#logger.error("USER DETAILS")
	info = {}
	main_response = {'code':0}

	json_response = {}

	user_email = request.GET['user']

	#user_detail = User.objects.get(email = user_email)
	query = "SELECT * FROM subdapp_user WHERE email = \"%s\"" % (user_email)

	cursor = connection.cursor()
	cursor.execute(query)
	result_user = cursor.fetchone()
	
	query = "SELECT su.email FROM subdapp_user_follow suf INNER JOIN subdapp_user su ON suf.from_user_id = su.id  WHERE suf.to_user_id = %s" % (result_user[0])	
	
	cursor.execute(query)	
	result_followers = cursor.fetchall()

	

	query = "SELECT su.email FROM subdapp_user_follow suf INNER JOIN subdapp_user su ON suf.to_user_id = su.id  WHERE suf.from_user_id = %s" % (result_user[0])	
	cursor.execute(query)	
	result_following = cursor.fetchall()

	query = "SELECT thread_id FROM subdapp_thread_subscribe  WHERE user_id = %s" % (result_user[0])	
	cursor.execute(query)	
	result_subscribe = cursor.fetchall()

	cursor.close()
	
	#main_response['response'] = get_user_info(user_detail)
	info['id'] = result_user[0]
	info['email'] = result_user[4]
	info['isAnonymous'] = result_user[3]

	if result_user[3] == False:
		info['name'] = result_user[1]
		info['username'] = result_user[2]
		info['about'] = result_user[5]
	else:
		info['name'] = None
		info['username'] = None
		info['about'] = None

	follower_list = []
	if len(result_followers) > 0:
		for follower in result_followers[0]:
			follower_list.append(follower)
	info['followers'] = follower_list

	following_list = []
	if len(result_following) > 0:
		for following in result_following[0]:
			following_list.append(following)
	info['following'] = following_list

	subscribe_list = []
	if len(result_subscribe) > 0:
		for subscribe in result_subscribe:
			subscribe_list.append(subscribe[0])

	info['subscriptions'] = subscribe_list
	#logger.error(result_subscribe)
	main_response['response'] = info
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

		query = "INSERT INTO subdapp_user_follow (from_user_id, to_user_id, to_email, from_email) VALUES (%s, %s, \"%s\", \"%s\")" % (follower_user.id, followee_user.id,follower_user.email, followee_user.email)

		cursor = connection.cursor()
		cursor.execute(query)
		connection.commit()
		cursor.close()

		#logger.error(follower_user)
		#logger.error(followee_user)

		# follower_user.follow.add(followee_user)

		main_response = {'code':0}

		json_response = get_user_info(follower_user)

	

	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

def user_unfollow(request):

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


		follower_user.follow.remove(followee_user)

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


		User_Post_Forum.objects.filter(user = user).update(name=user_name)
			#userpostforum.name = user_name
			#userpostforum.save(update_fields=['name'])
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

def user_listFollowing(request):
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

		following_list = []

		if (limit != 0) and (offset != 0):
			following_list = list(user.follow.values_list('email', flat=True).filter(id__gt=offset).order_by(sort_order)[:limit])
		else:
			following_list = list(user.follow.values_list('email', flat=True).filter().order_by(sort_order))
		
		out_list = []

		for following in following_list:
			following_user = User.objects.get(email = following)
			out_list.append(get_user_info(following_user))

		main_response = {'code':0}
		json_response = out_list
		
	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/user/listPosts/?since=2014-01-02+00%3A00%3A00&limit=2&user=example%40mail.ru&order=asc:
def user_listPosts(request):
	#logger.error("user_listFollowers")
	main_response = {}
	json_response = {}
	if request.method == 'GET':

		user_email = request.GET['user']
		order = request.GET['order']
		limit = request.GET.get('limit', 0)
		since = request.GET.get('since')

		#logger.error("reeaded")
		user = User.objects.get(email = user_email)

		if order == 'desc':
			sort_order = '-date'
		else:
			sort_order = 'date'

		post_list = []

		
		if (limit != 0):
			if since != None:
				post_list = list(Post.objects.values_list('id', flat=True).filter(user=user, date__gt=since).order_by(sort_order)[:limit])
			else:
				post_list = list(Post.objects.values_list('id', flat=True).filter(user=user).order_by(sort_order)[:limit])
		else:
			if since != None:
				post_list = list(Post.objects.values_list('id', flat=True).filter(user=user, date__gt=since).order_by(sort_order))
			else:
				post_list = list(Post.objects.values_list('id', flat=True).filter(user=user).order_by(sort_order))
		
		out_list = []

		for post_id in post_list:
			post_user = Post.objects.get(id = post_id)
			out_list.append(get_post_info(post_user, []))

		main_response = {'code':0}
		json_response = out_list
		
	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response