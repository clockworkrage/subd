# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from subdapp.models import User, Forum, Thread, Post, User_Post_Forum
import logging
import json
from django.db import connection
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.utils import dateformat
from django.conf import settings
#from user import get_user_info
#from thread import get_thread_info

logger = logging.getLogger(__name__)

def get_forum_info(forum_details):

	info = {}

	info['id']			= forum_details.id
	info['name']		= forum_details.name
	info['short_name']	= forum_details.short_name
	info['user']		= forum_details.user.email

	return info

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

def get_thread_info(thread_detail, related):
	info = {}

	info['date']		= dateformat.format(thread_detail.date, settings.DATETIME_FORMAT)
	info['dislikes']	= thread_detail.dislikes
	
	if find_list(related, 'forum'):
		info['forum']	= get_forum_info(thread_detail.forum)
	else:
		info['forum']	= thread_detail.forum.short_name

	info['id']			= thread_detail.id
	info['isClosed']	= thread_detail.isClosed
	info['isDeleted']	= thread_detail.isDeleted
	info['likes']		= thread_detail.likes
	info['message']		= thread_detail.message
	info['points']		= thread_detail.points
	info['posts']		= thread_detail.count
	if thread_detail.isDeleted == 1:
		info['posts'] = 0
	info['slug']		= thread_detail.slug
	info['title']		= thread_detail.title
	if find_list(related, 'user'):
		info['user']	= get_user_info(thread_detail.user)
	else:
		info['user']	= thread_detail.user.email
	
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
		#logger.error("post par det")
		#logger.error(post.parent)
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


def post_create(request):
	#logger.error("POST:")
	main_response = {'code':0}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body.decode('utf-8'))
		#logger.error("user_email")
		#logger.error(input_params)

		isApproved 		= input_params['isApproved']
		user_email 		= input_params['user']
		date 			= input_params['date']
		message 		= input_params['message']
		isSpam 			= input_params['isSpam']
		isHighlighted 	= input_params['isHighlighted']
		thread_id 		= input_params['thread']
		forum_name 		= input_params['forum']
		isDeleted 		= input_params['isDeleted']
		isEdited 		= input_params['isEdited']
		parent 			= input_params.get('parent', None)
		#logger.error(name)

		
		user = User.objects.get(email = user_email)
		#logger.error("GET1")
		thread = Thread.objects.get(id = thread_id)
		#logger.error("GET2")
		forum = Forum.objects.get(short_name = forum_name)
		#logger.error("GET3")
		post = Post(date = date, user = user, thread = thread, forum = forum, isApproved = isApproved, isHighlighted = isHighlighted, 
			isEdited = isEdited, isSpam = isSpam, isDeleted = isDeleted, message = message, parent = parent, short_name = forum_name, email = user_email)
		post.save()

		num_results = User_Post_Forum.objects.filter(user = user, short_name = forum.short_name).count()

		if num_results == 0:
			userpostforum = User_Post_Forum(user = user, short_name = forum.short_name, name = user.name)
			userpostforum.save()



		thread.count += 1
		thread.save(update_fields=['count'])

		
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



def post_details(request):
	
	main_response = {}
	json_response = {}
	if request.method == 'GET':

		post_id = request.GET['post']
		related = request.GET.get('related',[])
		try:
			main_response	= {'code':0}
			post = Post.objects.get(id = post_id)
			json_response	=	get_post_info(post, related)
		except Exception as e:
			return JsonResponse({'code':1, 'response': "error"})

		

		#logger.error("READED")
		# for temp in related:
		# 	if temp == 'user':
		# 		json_response['user'] = get_user_info(forum.user)
		# 	if temp == 'forum':
		# 		json_response['forum'] = get_user_info(forum.user)


	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/post/remove/ with {"post": 3}:
def post_remove(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body.decode('utf-8'))

		post_id = input_params['post']

		post = Post.objects.get(id = post_id)

		post.isDeleted = True

		post.save(update_fields=['isDeleted'])

		thread = Thread.objects.get(id = post.thread_id)
		thread.count -= 1
		thread.save(update_fields=['count'])

		main_response = {'code':0}

		json_response['post']	= post_id

	main_response['response'] = json_response;

	response = JsonResponse(main_response)

	return response

def post_restore(request):
		#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body.decode('utf-8'))

		post_id 	= input_params['post']

		post = Post.objects.get(id = post_id)

		post.isDeleted = False

		post.save(update_fields=['isDeleted'])

		thread = Thread.objects.get(id = post.thread_id)
		thread.count += 1
		thread.save(update_fields=['count'])

		main_response = {'code':0}

		json_response['post']	= post_id

	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/post/vote/ with {"vote": -1, "post": 5}:
def post_vote(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body.decode('utf-8'))
		
		#logger.error(request.body)
		post_id 	= input_params['post']
		vote = int(input_params['vote'])
		
		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		post = Post.objects.get(id = post_id)

		if vote == 1:
			post.likes += 1
			post.points = post.likes - post.dislikes
			post.save(update_fields=['likes', 'points'])
		else:
			post.dislikes += 1
			post.points = post.likes - post.dislikes
			post.save(update_fields=['dislikes', 'points'])

		main_response = {'code':0}

		json_response	=	get_post_info(post, [])

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/post/update/ with {"post": 3, "message": "my message 1"}:
def post_update(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body.decode('utf-8'))
		
		#logger.error(request.body)
		post_id 	= input_params['post']
		new_message = input_params['message']
		
		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		post = Post.objects.get(id = post_id)
		post.message = new_message
		post.save(update_fields=['message'])

		main_response = {'code':0}

		json_response	=	get_post_info(post, [])

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response


def post_list(request):
	#logger.error("result_posts")
	main_response = {}
	json_response = {}
	if request.method == 'GET':

		since_date = request.GET.get('since')

		#since = ' "%s" ' % since_date

		order = request.GET.get('order')
		limit = int(request.GET.get('limit', 0))
		forum_name = request.GET.get('forum', '')
		thread_id = request.GET.get('thread', '')

		post_list = []

		sort_order = " ORDER BY sp.date ASC"

		if order == 'desc':
			sort_order = " ORDER BY sp.date DESC"

		limit_string = ""

		if limit > 0:
			limit_string = "LIMIT %d" % limit

		since =""

		if since_date != None:
			since = " AND sp.date > \'%s\'" % since_date

		# if order == 'desc':
		# 	sort_order = '-date'
		# else:
		# 	sort_order = 'date'

		# if forum_name != '':
		# 	forum = Forum.objects.get(short_name = forum_name)
		# 	if limit != 0:
		# 			if since != None:
		# 				post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order)[:limit])
		# 			else:
		# 				post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum).order_by(sort_order)[:limit])
		# 	else:
		# 		if since != None:
		# 			post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order))
		# 		else:
		# 			post_list = list(Post.objects.values_list('id', flat=True).filter(forum=forum).order_by(sort_order))
		# if thread_id != '':
		# 	thread = Thread.objects.get(id = thread_id)
		# 	if limit != 0:
		# 		if since != None:
		# 			post_list = list(Post.objects.values_list('id', flat=True).filter(thread=thread, date__gt=since).order_by(sort_order)[:limit])
		# 		else:
		# 			post_list = list(Post.objects.values_list('id', flat=True).filter(thread=thread).order_by(sort_order)[:limit])
		# 	else:
		# 		if since != None:
		# 			post_list = list(Post.objects.values_list('id', flat=True).filter(thread=thread, date__gt=since).order_by(sort_order))
		# 		else:
		# 			post_list = list(Post.objects.values_list('id', flat=True).filter(thread=thread).order_by(sort_order))
		# out_list = []

		# for out_post_id in post_list:
		# 	out_post = Post.objects.get(id = out_post_id)
		# 	out_list.append(get_post_info(out_post,[]))

		# json_response	=	out_list

		params = ()
		query = ""
		out_list = []

		# if forum_name != '':
		# 	query = "SELECT sp.*, sf.short_name, su.email FROM subdapp_post sp INNER JOIN subdapp_forum sf ON sp.forum_id = sf.id \
		# 	INNER JOIN subdapp_user su ON sp.user_id = su.id \
		# 	WHERE sf.short_name = \"%s\"  \
		# 	%s %s %s" % (forum_name, since, sort_order, limit_string)
		# else:
		# 	query = "SELECT sp.*, sf.short_name, su.email FROM subdapp_post sp INNER JOIN subdapp_forum sf ON sp.forum_id = sf.id \
		# 	INNER JOIN subdapp_user su ON sp.user_id = su.id \
		# 	WHERE sp.thread_id = %s \
		# 	%s %s %s" % (thread_id, since, sort_order, limit_string)
		if forum_name != '':
			query = "SELECT id, date, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted, message, points, dislikes, likes, short_name, email, thread_id FROM subdapp_post sp \
			WHERE sp.short_name = \"%s\"  \
			%s %s %s" % (forum_name, since, sort_order, limit_string)
		else:
			query = "SELECT id, date, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted, message, points, dislikes, likes, short_name, email, thread_id  FROM subdapp_post sp \
			WHERE sp.thread_id = %s \
			%s %s %s" % (thread_id, since, sort_order, limit_string)
		#logger.error(query)
		#params = (forum_name, since, sort_order)
		cursor = connection.cursor()
		cursor.execute(query)
		result_posts = cursor.fetchall()
		
		cursor.close()

		if len(result_posts) > 0:
			for post_res in result_posts:
				#logger.error(post_res)
				info={}
				info['date']			= dateformat.format(post_res[1], settings.DATETIME_FORMAT)
				info['dislikes']		= post_res[10]
				info['forum']			= post_res[12]
				info['id']				= post_res[0]
				info['isApproved']		= post_res[3]
				info['isDeleted']		= post_res[7]
				info['isEdited']		= post_res[5]
				info['isHighlighted']	= post_res[4]
				info['isSpam']			= post_res[6]
				info['likes']			= post_res[11]
				info['message']			= post_res[8]
				info['parent']			= post_res[2]
				info['points']			= post_res[9]
				info['thread']	= post_res[14]
				info['user']	= post_res[13]
				out_list.append(info)

		json_response	=	out_list

		#logger.error(result_posts)

		main_response	= {'code':0}



	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response