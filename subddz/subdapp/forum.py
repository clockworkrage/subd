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
from user import get_user_info
from post import get_post_info
from thread import get_thread_info
from utils import check_dict

logger = logging.getLogger(__name__)
#Requesting http://some.host.ru/db/api/forum/create/ with {"name": "Forum With Sufficiently Large Name", "short_name": "forumwithsufficientlylargename", "user": "richard.nixon@example.com"}:

def get_forum_info(forum_details):

	info = {}

	info['id']	= forum_details.id
	info['name']	= forum_details.name
	info['short_name']	= forum_details.short_name
	info['user']	= forum_details.user.email

	return info

def forum_create(request):

	main_response = {'code':0}
	
	if request.method == 'POST':
		input_params = json.loads(request.body)


		name = input_params['name']
		short_name = input_params['short_name']
		user_email = input_params['user']
		

		user = User.objects.get(email = user_email)

		forum = Forum(name=name, short_name=short_name, user=user)
		forum.save()

		json_response = {}
		json_response['id'] = forum.id
		json_response['name'] = forum.name
		json_response['short_name'] = forum.short_name
		json_response['user'] = user.email


	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response
#http://some.host.ru/db/api/forum/details/?related=user&forum=forum3:
def forum_details(request):
	main_response = {}
	json_response = {}
	if request.method == 'GET':
		required = ['forum']

		try:
			check_dict(request.GET, required)
		except Exception as e:
			if e.message == 'required':
				return JsonResponse({'code':1, 'response': e.message})

		short_name = request.GET['forum']
		related = request.GET.get('related',[])

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
		since = request.GET.get('since', 0)
		order = request.GET['order']
		forum_name = request.GET['forum']
		limit = request.GET.get('limit', 0)
		related = request.GET.getlist('related')

		if order == 'desc':
			sort_order = '-date'
		else:
			sort_order = 'date'

		post_list = []

		forum = Forum.objects.get(short_name = forum_name)
		if since !=0:
			if limit != 0:
				post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order)[:limit])
			else:
				post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order))
		else:
			if limit != 0:
				post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum).order_by(sort_order)[:limit])
			else:
				post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum).order_by(sort_order))
		
		out_list = []


		for out_post_id in post_list:
			out_post = Post.objects.get(id = out_post_id)
			out_list.append(get_post_info(out_post, related))

		json_response = out_list


	main_response['response'] = json_response

	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/forum/listThreads/?related=forum&since=2013-12-31+00%3A00%3A00&order=desc&forum=forum1:
def forum_listThreads(request):

	main_response = {'code':0}
	
	if request.method == 'GET':
		since = request.GET.get('since')
		order = request.GET['order']
		forum_name = request.GET['forum']
		related = request.GET.getlist('related')

		if order == 'desc':
			sort_order = '-date'
		else:
			sort_order = 'date'

		thread_list = []

		forum = Forum.objects.get(short_name = forum_name)
		if since != None:
			thread_list = list(Thread.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order))
		else:
			thread_list = list(Thread.objects.values_list('id', flat=True).filter(forum=forum).order_by(sort_order))

		out_list = []


		for out_thread_id in thread_list:
			out_thread = Thread.objects.get(id = out_thread_id)
			out_list.append(get_thread_info(out_thread, related))

		json_response = out_list



	main_response['response'] = json_response

	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/forum/listUsers/?order=desc&forum=forum1:
def forum_listUsers(request):

	main_response = {'code':0}
	
	if request.method == 'GET':
		since = int(request.GET.get('since', 0))
		order = request.GET.get('order', 'DESC')
		limit = int(request.GET.get('limit', 0))
		forum_name = request.GET['forum']

		sort_order = ''
		limit_string = ''
		since_string = ''

		sort_order = " ORDER BY su.name ASC"

		if order == 'desc':
			sort_order = " ORDER BY su.name DESC"
		
		if limit > 0:
			limit_string = "LIMIT %d" % limit
		if since > 0:
			since_string = "AND su.id >= %d" % since
		user_list = []

		# forum = Forum.objects.get(short_name = forum_name)
		# user_list = list(Thread.objects.values_list('user', flat=True).filter(forum=forum)) #.order_by()

		out_list = []
		followers_list = []
		following_list = []
		subscribes_list = []
		# # for out_thread_id in thread_list:
		# # 	out_thread = Thread.objects.get(id = out_thread_id)
		# # 	out_list.append(get_thread_info(out_thread, related))
		cursor = connection.cursor()
		# query = "SELECT  subdapp_user.id FROM subdapp_user INNER JOIN subdapp_post ON subdapp_user.id = subdapp_post.user_id \
		# 	INNER JOIN subdapp_forum ON subdapp_post.forum_id = subdapp_forum.id \
		# 	WHERE subdapp_forum.short_name = \"%s\" %s \
		# 	GROUP BY subdapp_user.id \
		# 	%s %s " % (forum_name, since_string, sort_order, limit_string)
		query = "SELECT su.* FROM subdapp_user_post_forum supf INNER JOIN subdapp_user su ON supf.user_id = su.id \
			WHERE supf.short_name = \"%s\" %s %s %s" % (forum_name, since_string, sort_order, limit_string)
		cursor.execute(query)
		#forum_name, since_string,
		#logger.error("users_list_id")
		users_list_info = cursor.fetchall()

		if len(users_list_info) > 0:
			query_er = "SELECT su.email FROM subdapp_user_follow suf INNER JOIN subdapp_user su ON suf.from_user_id = su.id  WHERE suf.to_user_id = %s"	
			query_ing = "SELECT su.email FROM subdapp_user_follow suf INNER JOIN subdapp_user su ON suf.to_user_id = su.id  WHERE suf.from_user_id = %s"
			query_sub = "SELECT thread_id FROM subdapp_thread_subscribe  WHERE user_id = %s"
			for user_follow in users_list_info:
				params = user_follow[0]
				cursor.execute(query_er, params)
				result_followers = cursor.fetchall()
				followers_list.append(result_followers)

				cursor.execute(query_ing, params)
				result_following = cursor.fetchall()
				following_list.append(result_following)

				cursor.execute(query_sub, params)	
				result_subscribe = cursor.fetchall()
				subscribes_list.append(result_subscribe)

		cursor.close()

		#logger.error("users_list_id")
		#logger.error(followers_list)
		#logger.error(following_list)
		logger.error(subscribes_list)

		
		#user_id_list = []
		index = 0;
		if len(users_list_info) > 0:
			for user_info in users_list_info:
				info={}
				follower_res = []
				following_res = []
				subscribes_res = []
				info['id'] = user_info[0]

				if user_info[3] == False:
					info['about'] = user_info[5]
					info['username'] = user_info[2]
					info['name'] = user_info[1]
				else:
					info['about'] = None
					info['username'] = None
					info['name'] = None


				for follower in followers_list[index]:
					follower_res.append(follower)
				info['followers'] = follower_res

				for following in following_list[index]:
					following_res.append(following)
				info['following'] = following_res


				#if len(subscribes_list[index]) > 0:
				for subscribe in subscribes_list[index]:
					logger.error(subscribe)
					subscribes_res.append(subscribe[0])
				# else:
				# 	subscribes_res.append(())
				info['subscriptions'] = subscribes_res

				info['isAnonymous'] = user_info[3]
				info['email'] = user_info[4]
		 		out_list.append(info)
		 		index =index + 1

		#for row in cursor.fetchall():
		#	user_list.append(row[0])


		# for out_user_id in user_id_list:
		#  	out_user = User.objects.get(id = out_user_id)
		#  	out_list.append(get_user_info(out_user))

		json_response = out_list


	main_response['response'] = json_response

	response = JsonResponse(main_response)

	return response