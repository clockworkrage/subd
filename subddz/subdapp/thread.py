# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from subdapp.models import User, Forum, Thread, Post, User_Thread
import json
from django.db import connection
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.utils import dateformat
from django.conf import settings
from user import get_user_info


def find_list(search_list, value):

	for element in search_list:
		if element == value:
			return True;

	return False

def get_forum_info(forum_details):

	info = {}

	info['id']			= forum_details.id
	info['name']		= forum_details.name
	info['short_name']	= forum_details.short_name
	info['user']		= forum_details.user.email

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
		
		forum_name 	= input_params['forum']
		title 		= input_params['title']
		isClosed 	= input_params['isClosed']
		user_email 	= input_params['user']
		thread_date = input_params['date']
		message 	= input_params['message']
		slug 		= input_params['slug']	
		isDeleted 	= input_params['isDeleted']

		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		user = User.objects.get(email = user_email)
		forum = Forum.objects.get(short_name = forum_name)

		thread = Thread (date = thread_date, user =user, forum = forum, title = title, slug = slug, message = message,
			isClosed = isClosed, isDeleted = isDeleted)
		thread.save()

		#num_results = User_Post_Forum.objects.filter(user = user, short_name = forum.short_name).count()
		userthread = User_Thread(short_name = forum.short_name, thread_id = thread.id, email = user_email, count = 0)
		userthread.save()

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
	info['posts']		= Post.objects.filter(thread = thread_detail, isDeleted = False).count()
	info['slug']		= thread_detail.slug
	info['title']		= thread_detail.title
	if find_list(related, 'user'):
		info['user']	= get_user_info(thread_detail.user)
	else:
		info['user']	= thread_detail.user.email
	
	return info

def thread_details(request):
	#logger.error("THREAD DETAILS:")
	main_response = {}
	json_response = {}
	if request.method == 'GET':

		thread_id = request.GET['thread']
		related = request.GET.getlist('related')

		if 'thread' in related:
			return JsonResponse({'code':3, 'response': 'error'})

		thread = Thread.objects.get(id = thread_id)

		main_response	= {'code':0}
		json_response	= get_thread_info(thread, related)
		#logger.error("READED")
		# for temp in related:
		# 	if temp == 'user':
		# 		json_response['user'] = get_user_info(forum.user)
		# 	if temp == 'forum':
		# 		json_response['forum'] = get_user_info(forum.user)


	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response


# Requesting http://some.host.ru/db/api/thread/subscribe/ with {"user": "richard.nixon@example.com", "thread": 4}:
def thread_subscribe(request):
	#logger.error("THREAD:")
	main_response = {'code':0}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		
		#logger.error(request.body)
		
		thread_id 	= input_params['thread']
		user_email 	= input_params['user']
		

		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		user = User.objects.get(email = user_email)
		thread = Thread.objects.get(id = thread_id)

		thread.subscribe.add(user)

		json_response['id'] = thread.id
		json_response['date'] = user_email

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

def thread_unsubscribe(request):
	#logger.error("THREAD:")
	main_response = {'code':0}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		
		#logger.error(request.body)
		
		thread_id 	= input_params['thread']
		user_email 	= input_params['user']
		

		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		user = User.objects.get(email = user_email)
		thread = Thread.objects.get(id = thread_id)

		thread.subscribe.remove(user)

		json_response['id'] = thread.id
		json_response['date'] = user_email

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/thread/update/ with {"message": "hey hey hey hey!", "slug": "newslug", "thread": 1}:
def thread_update(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		
		#logger.error(request.body)
		thread_id 	= input_params['thread']
		new_message = input_params['message']
		new_slug 	= input_params['slug']
		

		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		thread = Thread.objects.get(id = thread_id)
		thread.message = new_message
		thread.slug = new_slug
		thread.save(update_fields=['message', 'slug'])

		main_response = {'code':0}

		json_response	=	get_thread_info(thread, [])

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/thread/vote/ with {"vote": 1, "thread": 1}:
def thread_vote(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		
		#logger.error(request.body)
		thread_id 	= input_params['thread']
		vote = int(input_params['vote'])
		
		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		thread = Thread.objects.get(id = thread_id)

		if vote == 1:
			thread.likes += 1
			thread.points = thread.likes - thread.dislikes
			thread.save(update_fields=['likes', 'points'])
		else:
			thread.dislikes += 1
			thread.points = thread.likes - thread.dislikes
			thread.save(update_fields=['dislikes', 'points'])

		main_response = {'code':0}

		json_response	=	get_thread_info(thread, [])

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/thread/close/ with {"thread": 1}:
def thread_close(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		
		#logger.error(request.body)
		thread_id 	= input_params['thread']

		
		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		thread = Thread.objects.get(id = thread_id)

		thread.isClosed = True

		thread.save(update_fields=['isClosed'])

		main_response = {'code':0}

		json_response['thread']	= thread_id

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

def thread_open(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		
		#logger.error(request.body)
		thread_id 	= input_params['thread']

		#logger.error("DONE")
		#logger.error(thread_date)
		#try:
		thread = Thread.objects.get(id = thread_id)

		thread.isClosed = False

		thread.save(update_fields=['isClosed'])

		main_response = {'code':0}

		json_response['thread']	= thread_id

	#logger.error("Done")
	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

def thread_remove(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)

		thread_id 	= input_params['thread']

		thread = Thread.objects.get(id = thread_id)

		thread.isDeleted = True

		thread.save(update_fields=['isDeleted'])

		cursor = connection.cursor()
		cursor.execute("UPDATE subdapp_post SET isDeleted=1 WHERE thread_id=%s",[thread.id])
		connection.commit()
		cursor.close()
		
		main_response = {'code':0}

		json_response['thread']	= thread_id

	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response

def thread_restore(request):
	#logger.error("THREAD:")
	main_response = {}
	json_response = {}
	if request.method == 'POST':
		input_params = json.loads(request.body)
		

		thread_id 	= input_params['thread']

		thread = Thread.objects.get(id = thread_id)

		thread.isDeleted = False

		thread.save(update_fields=['isDeleted'])

		cursor = connection.cursor()
		cursor.execute("UPDATE subdapp_post SET isDeleted=0 WHERE thread_id=%s",[thread.id])
		connection.commit()
		cursor.close()

		main_response = {'code':0}

		json_response['thread']	= thread_id

	main_response['response'] = json_response;
	response = JsonResponse(main_response)

	return response


#Requesting http://some.host.ru/db/api/thread/list/?since=2014-01-01+00%3A00%3A00&order=desc&forum=forum1:
def thread_list(request):

	main_response = {}
	json_response = {}
	if request.method == 'GET':

		since_date = request.GET.get('since')
		order = request.GET.get('order')
		limit = int(request.GET.get('limit', 0))
		forum_name = request.GET.get('forum', '')
		user_email = request.GET.get('user', '')

		# if order == 'desc':
		# 	sort_order = '-date'
		# else:
		# 	sort_order = 'date'
		# if forum_name != '':
		# 	forum = Forum.objects.get(short_name = forum_name)
		# 	if since != None:
		# 		thread_list = list(Thread.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order))
		# 	else:
		# 		thread_list = list(Thread.objects.values_list('id', flat=True).filter(forum=forum).order_by(sort_order))
		# if user_email != '':
		# 	user = User.objects.get(email = user_email)
		# 	if since != None:
		# 		thread_list = list(Thread.objects.values_list('id', flat=True).filter(user=user, date__gt=since).order_by(sort_order))
		# 	else:
		# 		thread_list = list(Thread.objects.values_list('id', flat=True).filter(user=user).order_by(sort_order))

		sort_order = " ORDER BY st.date ASC"

		if order == 'desc':
			sort_order = " ORDER BY st.date DESC"

		limit_string = ""

		if limit > 0:
			limit_string = "LIMIT %d" % limit

		since =""

		if since_date != None:
			since = " AND st.date > \'%s\'" % since_date

		out_list = []

		query = ""

		if forum_name != '':
			query = "SELECT st.*, sut.short_name, sut.email, sut.count  FROM subdapp_thread st  INNER JOIN  subdapp_user_thread sut ON st.id = sut.thread_id WHERE sut.short_name = \"%s\" \
			%s %s %s" % (forum_name, since, sort_order, limit_string)
		else:
			query = "SELECT st.*, sut.short_name, sut.email, sut.count   FROM subdapp_thread st  INNER JOIN  subdapp_user_thread sut ON st.id = sut.thread_id WHERE sut.email = \"%s\"  \
			%s %s %s" % (user_email, since, sort_order, limit_string)

		cursor = connection.cursor()
		cursor.execute(query)
		result_threads = cursor.fetchall()
		cursor.close()
		out_list = []

		# for out_thread_id in thread_list:
		# 	out_thread = Thread.objects.get(id = out_thread_id)
		# 	out_list.append(get_thread_info(out_thread, []))
		if len(result_threads) > 0:
			for thread_res in result_threads:
				#logger.error(post_res)
				info={}
				info['date']		= dateformat.format(thread_res[1], settings.DATETIME_FORMAT)
				info['dislikes']	= thread_res[9]
				info['forum']	= thread_res[12]
				info['id']			= thread_res[0]
				info['isClosed']	= thread_res[5]
				info['isDeleted']	= thread_res[6]
				info['likes']		= thread_res[11]
				info['message']		= thread_res[4]
				info['points']		= thread_res[10]
				info['posts']		= thread_res[14]
				info['slug']		= thread_res[3]
				info['title']		= thread_res[2]
				info['user']	= thread_res[13]

				out_list.append(info)

		main_response = {'code':0}
		json_response = out_list
		
	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/thread/listPosts/?since=2014-01-02+00%3A00%3A00&limit=2&order=asc&thread=3:
def thread_listPosts(request):

	main_response = {}
	json_response = {}
	if request.method == 'GET':

		thread_id = request.GET.get('thread', 0)
		limit = int(request.GET.get('limit', 0))
		sort_type = request.GET.get('sort', 'flat')
		order = request.GET.get('order', 'desc')
		since_date = request.GET.get('since')

		# post_list = []
		# sort_order = ''
		# if order == 'desc':
		# 	sort_order = '-date'
		# else:
		# 	sort_order = 'date'
		# if since != 0:
		# 	post_list = list(Post.objects.values_list('id', flat=True).filter(thread_id=thread_id, date__gt=since).order_by(sort_order))
		# else:
		# 	post_list = list(Post.objects.values_list('id', flat=True).filter(thread_id=thread_id).order_by(sort_order))
		# out_list = []



		# for out_post_id in post_list:
		# 	out_post = Post.objects.get(id = out_post_id)
		# 	out_list.append(get_post_info(out_post, []))

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

		out_list = []

		query = "SELECT sp.*, supt.short_name, supt.email   FROM subdapp_post sp  INNER JOIN  subdapp_user_post_thread supt ON sp.id = supt.post_id WHERE sp.thread_id = %s  \
		%s %s %s" % (thread_id, since, sort_order, limit_string)

		cursor = connection.cursor()
		cursor.execute(query)
		result_posts = cursor.fetchall()
		cursor.close()

		if len(result_posts) > 0:
			for post_res in result_posts:
				#logger.error(post_res)
				info={}
				info['date']			= dateformat.format(post_res[1], settings.DATETIME_FORMAT)
				info['dislikes']		= post_res[12]
				info['forum']			= post_res[15]
				info['id']				= post_res[0]
				info['isApproved']		= post_res[3]
				info['isDeleted']		= post_res[7]
				info['isEdited']		= post_res[5]
				info['isHighlighted']	= post_res[4]
				info['isSpam']			= post_res[6]
				info['likes']			= post_res[14]
				info['message']			= post_res[8]
				info['parent']			= post_res[2]
				info['points']			= post_res[13]
				info['thread']	= post_res[10]
				info['user']	= post_res[16]
				out_list.append(info)

		main_response = {'code':0}
		json_response = out_list
		
	main_response['response'] = json_response
	response = JsonResponse(main_response)

	return response