from django.db import models

# Create your models here.
class User(models.Model):
	name = models.CharField(max_length = 50, default='name')
	username = models.CharField(max_length = 50, default='username')
	isAnonymous = models.BooleanField(default=False)
	email = models.CharField(max_length = 50, default='email')
	about = models.TextField(max_length = 700, default='about')

	def __unicode__(self):
		return self.email

class Forum(models.Model):
	name = models.CharField(max_length = 100, default='forumname')
	short_name = models.CharField(max_length = 50, default='shortforumname')
	user = models.ForeignKey(User)

	def __unicode__(self):
		return self.short_name

class Thread(models.Model):
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)
	forum = models.ForeignKey(Forum)
	title = models.CharField(max_length = 50, default='title')
	slug = models.CharField(max_length = 50, default='title')
	message = models.CharField(max_length = 150, default='message')
	isClosed = models.BooleanField(default=False)
	isDeleted = models.BooleanField(default=False)
	

	def __unicode__(self):
		return self.title

class Post(models.Model):
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)
	thread = models.ForeignKey(Thread)
	forum = models.ForeignKey(Forum)
	parent = models.IntegerField(default=None)
	isApproved = models.BooleanField(default=False)
	isHighlighted = models.BooleanField(default=False)
	isEdited = models.BooleanField(default=False)
	isSpam = models.BooleanField(default=False)
	isDeleted = models.BooleanField(default=False)
	message = models.TextField(max_length = 500, default='message')
	

	def __unicode__(self):
		return self.message