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
from user import get_user_info
from post import get_post_info

logger = logging.getLogger(__name__)
#Requesting http://some.host.ru/db/api/forum/create/ with {"name": "Forum With Sufficiently Large Name", "short_name": "forumwithsufficientlylargename", "user": "richard.nixon@example.com"}:

def get_forum_info(forum_details):

	info = {}

	info['id']			= forum_details.id
	info['name']		= forum_details.name
	info['short_name']	= forum_details.short_name
	info['user']		= forum_details.user.email

	return info

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

#Requesting 
#http://some.host.ru/db/api/forum/listPosts/?related=thread&related=forum&since=2014-01-01+00%3A00%3A00&order=desc&forum=forum1:
def forum_listPosts(request):

	main_response = {'code':0}
	
	if request.method == 'GET':
		#logger.error("user_email")
		#logger.error(request.body)
		since = request.GET['since']
		order = request.GET['order']
		forum_name = request.GET['forum']
		related = request.GET.get('related', [])

		if order == 'desc':
			sort_order = '-date'
		else:
			sort_order = 'date'

		post_list = []

		forum = Forum.objects.get(short_name = forum_name)
		post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order))

		out_list = []

		#logger.error("user_email22")
		#logger.error(name)
		#logger.error(user)
		for out_post_id in post_list:
			out_post = Post.objects.get(id = out_post_id)
			out_list.append(get_post_info(out_post, related))

		json_response = out_list


	#logger.error("Done")
	main_response['response'] = json_response

	response = JsonResponse(main_response)

	return response