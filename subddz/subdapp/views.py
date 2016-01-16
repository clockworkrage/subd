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

def clear(request):

	# cursor = connection.cursor()

	# cursor.execute("DELETE FROM subdapp_forum")
	# connection.commit()
	# cursor.execute("DELETE FROM subdapp_user_follow")
	# connection.commit()

	# cursor.execute("DELETE FROM subdapp_thread_subscribe")
	# connection.commit()
	
	# cursor.execute("DELETE FROM subdapp_user;")
	# connection.commit()

	# cursor.execute("DELETE FROM subdapp_forum") 
	# connection.commit()

	# cursor.execute("DELETE FROM subdapp_thread")
	# connection.commit()

	# cursor.execute("DELETE FROM subdapp_post")
	# connection.commit()
	User.objects.all().delete()
	Forum.objects.all().delete()
	Thread.objects.all().delete()
	Post.objects.all().delete()
	User_Post_Forum.objects.all().delete()
	
	main_responce = {'code':0}
	main_responce['response'] = "OK"

	response = JsonResponse(main_responce)
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
