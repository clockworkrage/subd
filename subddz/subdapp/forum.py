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
#from user import get_user_info
#from post import get_post_info
#from thread import get_thread_info
#from utils import check_dict


#Requesting http://some.host.ru/db/api/forum/create/ with {"name": "Forum With Sufficiently Large Name", "short_name": "forumwithsufficientlylargename", "user": "richard.nixon@example.com"}:
logger = logging.getLogger(__name__)

def check_dict(data, keys):
	for key in keys:
		if key not in data:
			raise Exception('required')
	return

def find_list(search_list, value):

	for element in search_list:
		if element == value:
			return True
	return False



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
		input_params = json.loads(request.body.decode('utf-8'))


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
		since_date = request.GET.get('since')
		order = request.GET['order']
		forum_name = request.GET['forum']
		limit = int(request.GET.get('limit', 0))
		related = request.GET.getlist('related')

		user_related = False
		forum_related = False
		thread_related = False

		if find_list(related, 'user'):
			user_related = True
		if find_list(related, 'forum'):
			forum_related = True
		if find_list(related, 'thread'):
			thread_related = True

		# if order == 'desc':
		# 	sort_order = '-date'
		# else:
		# 	sort_order = 'date'

		# post_list = []

		# if since !=0:
		# 	if limit != 0:
		# 		post_list = list(Post.objects.values_list('id', flat=True).filter(short_name=forum_name, date__gt=since).order_by(sort_order))
		# 	else:
		# 		post_list = list(Post.objects.values_list('id', flat=True).filter(short_name=forum_name, date__gt=since).order_by(sort_order))
		# else:
		# 	if limit != 0:
		# 		post_list = list(Post.objects.values_list('id', flat=True).filter(short_name=forum_name).order_by(sort_order))
		# 	else:
		# 		post_list = list(Post.objects.values_list('id', flat=True).filter(short_name=forum_name).order_by(sort_order))
		
		# out_list = []
		user_forum_info_list = []
		followers_list = []
		following_list = []
		subscribes_list = []

		limit_string = ""

		if limit > 0:
			limit_string = "LIMIT %d" % limit

		sort_order = " ORDER BY sp.date ASC"

		if order == 'desc':
			sort_order = " ORDER BY sp.date DESC"

		since =""

		if since_date != None:
			since = " AND sp.date > \'%s\'" % since_date

		out_list = []

		user_forum_info_list = []
		followers_list = []
		following_list = []
		subscribes_list = []
		thread_list = []

		query = "SELECT id, date, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted, message, points, dislikes, likes, short_name, email, thread_id, user_id \
		  FROM subdapp_post sp  WHERE sp.short_name = \"%s\" \
			%s %s %s" % (forum_name, since, sort_order, limit_string)

		cursor = connection.cursor()
		cursor.execute(query)
		result_posts = cursor.fetchall()
		
		if user_related == True:
			if len(result_posts) > 0:
				query_er = "SELECT suf.to_email FROM subdapp_user_follow suf  WHERE suf.to_user_id = %s"	
				query_ing = "SELECT suf.from_email FROM subdapp_user_follow suf WHERE suf.from_user_id = %s"
				query_sub = "SELECT thread_id FROM subdapp_thread_subscribe  WHERE user_id = %s"
				query = "SELECT * FROM subdapp_user WHERE id = \"%s\""

				
				for user_post in result_posts:
					params = (user_post[15],)


					cursor.execute(query, params)
					res_usr_info = cursor.fetchone()		
					user_forum_info_list.append(res_usr_info)

					cursor.execute(query_er, params)
					result_followers = cursor.fetchall()
					followers_list.append(result_followers)

					cursor.execute(query_ing, params)
					result_following = cursor.fetchall()
					following_list.append(result_following)

					cursor.execute(query_sub, params)	
					result_subscribe = cursor.fetchall()
					subscribes_list.append(result_subscribe)

		if thread_related == True:
			if len(result_posts) > 0:
				query = "SELECT id, date, title, slug, message, isClosed, isDeleted, points, dislikes, likes, count, short_name, email  FROM subdapp_thread st  WHERE st.id = %s "

				for thread_post in result_posts:
					params = (thread_post[14],)

					cursor.execute(query, params)
					res_thr_info = cursor.fetchone()		
					thread_list.append(res_thr_info)

		cursor.close()

		if forum_related == True:
			forum_details = Forum.objects.get(short_name = forum_name)

		
		index = 0
		if len(result_posts) > 0:
			for post_res in result_posts:
				#logger.error(post_res)
				info={}
				info['date']			= dateformat.format(post_res[1], settings.DATETIME_FORMAT)
				info['dislikes']		= post_res[10]
				if forum_related == True:
					info['forum']	= get_forum_info(forum_details)
				else:
					info['forum']	= post_res[12]
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

				if thread_related == False:
					info['thread']	= post_res[14]
				else:
					post_thread_info = {}
					post_thread_info['date']		= dateformat.format(thread_list[index][1], settings.DATETIME_FORMAT)
					post_thread_info['dislikes']	= thread_list[index][8]
					post_thread_info['forum']	= thread_list[index][11]
					post_thread_info['id']			= thread_list[index][0]
					post_thread_info['isClosed']	= thread_list[index][5]
					post_thread_info['isDeleted']	= thread_list[index][6]
					post_thread_info['likes']		= thread_list[index][9]
					post_thread_info['message']		= thread_list[index][4]
					post_thread_info['points']		= thread_list[index][7]
					post_thread_info['posts']		= thread_list[index][10]
					post_thread_info['slug']		= thread_list[index][3]
					post_thread_info['title']		= thread_list[index][2]
					post_thread_info['user']		= thread_list[index][12]

					info['thread'] = post_thread_info

				if user_related == False:
					info['user']	= post_res[13]
				else:
					main_user_info={}
					follower_res = []
					following_res = []
					subscribes_res = []

					main_user_info['id'] = user_forum_info_list[index][0]

					if user_forum_info_list[index][3] == False:
						main_user_info['about'] = user_forum_info_list[index][5]
						main_user_info['username'] = user_forum_info_list[index][2]
						main_user_info['name'] = user_forum_info_list[index][1]
					else:
						main_user_info['about'] = None
						main_user_info['username'] = None
						main_user_info['name'] = None


					for follower in followers_list[index]:
						follower_res.append(follower)
					main_user_info['followers'] = follower_res

					for following in following_list[index]:
						following_res.append(following)
					main_user_info['following'] = following_res


					#if len(subscribes_list[index]) > 0:
					for subscribe in subscribes_list[index]:
						#logger.error(subscribe)
						subscribes_res.append(subscribe[0])
					# else:
					# 	subscribes_res.append(())
					main_user_info['subscriptions'] = subscribes_res

					main_user_info['isAnonymous'] = user_forum_info_list[index][3]
					main_user_info['email'] = user_forum_info_list[index][4]
					info['user'] = main_user_info

				out_list.append(info)
				index += 1
		# for out_post_id in post_list:
		# 	out_post = Post.objects.get(id = out_post_id)
		# 	out_list.append(get_post_info(out_post, related))



		json_response = out_list


	main_response['response'] = json_response

	response = JsonResponse(main_response)

	return response

#Requesting http://some.host.ru/db/api/forum/listThreads/?related=forum&since=2013-12-31+00%3A00%3A00&order=desc&forum=forum1:
def forum_listThreads(request):

	main_response = {'code':0}
	
	if request.method == 'GET':
		since_date = request.GET.get('since')
		order = request.GET['order']
		forum_name = request.GET.get('forum', '')
		related = request.GET.getlist('related')
		limit = int(request.GET.get('limit', 0))

		user_related = False
		forum_related = False

		if find_list(related, 'user'):
			user_related = True
		if find_list(related, 'forum'):
			forum_related = True

		# if order == 'desc':
		# 	sort_order = '-date'
		# else:
		# 	sort_order = 'date'

		# thread_list = []

		# forum = Forum.objects.get(short_name = forum_name)
		# if since != None:
		# 	thread_list = list(Thread.objects.values_list('id', flat=True).filter(forum=forum, date__gt=since).order_by(sort_order))
		# else:
		# 	thread_list = list(Thread.objects.values_list('id', flat=True).filter(forum=forum).order_by(sort_order))

		#out_list = []
		limit_string = ""

		if limit > 0:
			limit_string = "LIMIT %d" % limit

		sort_order = " ORDER BY st.date ASC"

		if order == 'desc':
			sort_order = " ORDER BY st.date DESC"

		since =""

		if since_date != None:
			since = " AND st.date > \'%s\'" % since_date

		out_list = []


		user_forum_info_list = []
		followers_list = []
		following_list = []
		subscribes_list = []

		query = "SELECT id, date, title, slug, message, isClosed, isDeleted, points, dislikes, likes, count, short_name, email, user_id  FROM subdapp_thread st  WHERE st.short_name = \"%s\" \
			%s %s %s" % (forum_name, since, sort_order, limit_string)

		
		cursor = connection.cursor()
		cursor.execute(query)
		result_threads = cursor.fetchall()
		
		if user_related == True:
			if len(result_threads) > 0:
				query_er = "SELECT suf.to_email FROM subdapp_user_follow suf  WHERE suf.to_user_id = %s"	
				query_ing = "SELECT suf.from_email FROM subdapp_user_follow suf WHERE suf.from_user_id = %s"
				query_sub = "SELECT thread_id FROM subdapp_thread_subscribe  WHERE user_id = %s"
				query = "SELECT * FROM subdapp_user WHERE id = \"%s\""

				
				for user_thread in result_threads:
					params = (user_thread[13],)

					#logger.error(user_thread[13])

					cursor.execute(query, params)
					res_usr_info = cursor.fetchone()		
					user_forum_info_list.append(res_usr_info)

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
		# forum_details = None

		if forum_related == True:
			forum_details = Forum.objects.get(short_name = forum_name)

		
		index = 0
		if len(result_threads) > 0:
			for thread_res in result_threads:
				#logger.error(post_res)
				info={}
				info['date']		= dateformat.format(thread_res[1], settings.DATETIME_FORMAT)
				info['dislikes']	= thread_res[8]
				#info['forum']	= thread_res[11]
				if forum_related == True:
					info['forum']	= get_forum_info(forum_details)
				else:
					info['forum']	= thread_res[11]

				info['id']			= thread_res[0]
				info['isClosed']	= thread_res[5]
				info['isDeleted']	= thread_res[6]
				info['likes']		= thread_res[9]
				info['message']		= thread_res[4]
				info['points']		= thread_res[7]
				info['posts']		= thread_res[10]
				info['slug']		= thread_res[3]
				info['title']		= thread_res[2]

				if user_related == False:
					info['user']	= thread_res[12]
				else:
					main_user_info={}
					follower_res = []
					following_res = []
					subscribes_res = []

					main_user_info['id'] = user_forum_info_list[index][0]

					if user_forum_info_list[index][3] == False:
						main_user_info['about'] = user_forum_info_list[index][5]
						main_user_info['username'] = user_forum_info_list[index][2]
						main_user_info['name'] = user_forum_info_list[index][1]
					else:
						main_user_info['about'] = None
						main_user_info['username'] = None
						main_user_info['name'] = None


					for follower in followers_list[index]:
						follower_res.append(follower)
					main_user_info['followers'] = follower_res

					for following in following_list[index]:
						following_res.append(following)
					main_user_info['following'] = following_res


					#if len(subscribes_list[index]) > 0:
					for subscribe in subscribes_list[index]:
						#logger.error(subscribe)
						subscribes_res.append(subscribe[0])
					# else:
					# 	subscribes_res.append(())
					main_user_info['subscriptions'] = subscribes_res

					main_user_info['isAnonymous'] = user_forum_info_list[index][3]
					main_user_info['email'] = user_forum_info_list[index][4]
					info['user'] = main_user_info

				out_list.append(info)
				index += 1

		# for out_thread_id in thread_list:
		# 	out_thread = Thread.objects.get(id = out_thread_id)
		# 	out_list.append(get_thread_info(out_thread, related))

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

		sort_order = " ORDER BY supf.name ASC"

		if order == 'desc':
			sort_order = " ORDER BY supf.name DESC"
		
		if limit > 0:
			limit_string = "LIMIT %d" % limit
		if since > 0:
			since_string = "AND supf.id >= %d" % since
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
			query_er = "SELECT suf.to_email FROM subdapp_user_follow suf  WHERE suf.to_user_id = %s"	
			query_ing = "SELECT suf.from_email FROM subdapp_user_follow suf WHERE suf.from_user_id = %s"
			query_sub = "SELECT thread_id FROM subdapp_thread_subscribe  WHERE user_id = %s"
			for user_follow in users_list_info:
				params = (user_follow[0],)
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
		#logger.error(subscribes_list)

		
		#user_id_list = []
		index = 0
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
					#logger.error(subscribe)
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