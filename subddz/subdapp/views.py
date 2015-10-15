from django.shortcuts import render
from django.http import JsonResponse
from subdapp.models import User, Forum, Thread, Post
import logging
import json

logger = logging.getLogger(__name__)

def index(request):
	
	response = JsonResponse({'foo': 'bar'})
	return response

def user_create(request):

	main_responce = {'code':'0'}

	if request.method == 'POST':
		for key in request.POST:
			logger.error(key)
		about = request.POST.get('about', "about")
		email = request.POST.get('email', "email")
		name = request.POST.get('name', "name")
		isAnon = request.POST.get('isAnonymous', False)
		username = request.POST.get('username', "username")

		

		user = User(name=name, username=username, isAnonymous=isAnon, email=email, about=about)
		user.save()



		json_response = {}
		json_response['about'] = user.about
		json_response['email'] = user.email
		json_response['id'] = user.id
		json_response['isAnonymous'] = user.isAnonymous
		json_response['name'] = user.name
		json_response['username'] = user.username

	main_responce['response'] = json_response;
	response = JsonResponse(main_responce)

	return response

def clear(request):
	
	main_responce = {'code':'0'}
	main_responce['response'] = "OK"

	response = JsonResponse(main_responce)
	return response