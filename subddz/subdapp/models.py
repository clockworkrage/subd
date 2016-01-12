from django.db import models


class User(models.Model):
	name = models.CharField(max_length = 50, null=True)
	username = models.CharField(max_length = 50, null=True)
	isAnonymous = models.BooleanField(default=False)
	email = models.CharField(max_length = 50, null=True)
	about = models.TextField(max_length = 700, default='about')
	follow = models.ManyToManyField("self", symmetrical=False)

	def __unicode__(self):
		return self.email

class Forum(models.Model):
	name = models.CharField(max_length = 100, default='forumname')
	short_name = models.CharField(max_length = 50, default='shortforumname')
	user = models.ForeignKey(User)

	def __unicode__(self):
		return self.short_name

class User_Post_Forum(models.Model):
	short_name = models.CharField(max_length = 50, default='shortforumname')
	user = models.ForeignKey(User)
	def __unicode__(self):
		return self.short_name

class User_Post_Thread(models.Model):
	post_id = models.IntegerField(default=0)
	email = models.CharField(max_length = 50, null=True)
	short_name = models.CharField(max_length = 50, default='shortforumname')
	thread_id = models.IntegerField(default=0)
	def __unicode__(self):
		return self.short_name

class User_Thread(models.Model):
	email = models.CharField(max_length = 50, null=True)
	short_name = models.CharField(max_length = 50, default='shortforumname')
	thread_id = models.IntegerField(default=0)
	count = models.IntegerField(default=0)
	def __unicode__(self):
		return self.email

class Thread(models.Model):
	date 		= models.DateTimeField(auto_now=False, auto_now_add=False)
	user 		= models.ForeignKey(User, related_name='%(class)s_user_create')
	forum 		= models.ForeignKey(Forum)
	title 		= models.CharField(max_length = 50, default='title')
	slug 		= models.CharField(max_length = 50, default='title')
	message 	= models.TextField(max_length = 500, default='message')
	isClosed 	= models.BooleanField(default=False)
	isDeleted 	= models.BooleanField(default=False)
	subscribe 	= models.ManyToManyField(User, related_name='%(class)s_user_subs')
	points 		= models.IntegerField(default=0)
	dislikes 	= models.IntegerField(default=0)
	likes 		= models.IntegerField(default=0)
	

	def __unicode__(self):
		return self.title

class Post(models.Model):
	date 			= models.DateTimeField(auto_now=False, auto_now_add=False)
	user 			= models.ForeignKey(User)
	thread 			= models.ForeignKey(Thread)
	forum 			= models.ForeignKey(Forum)
	parent 			= models.IntegerField(default=None, null=True)
	isApproved 		= models.BooleanField(default=False)
	isHighlighted 	= models.BooleanField(default=False)
	isEdited 		= models.BooleanField(default=False)
	isSpam 			= models.BooleanField(default=False)
	isDeleted 		= models.BooleanField(default=False)
	message 		= models.TextField(max_length = 500, default='message')
	points 			= models.IntegerField(default=0)
	dislikes 		= models.IntegerField(default=0)
	likes 			= models.IntegerField(default=0)
	

	def __unicode__(self):
		return self.message
