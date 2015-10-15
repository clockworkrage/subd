# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'forumname', max_length=100)),
                ('short_name', models.CharField(default=b'shortforumname', max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('parent', models.IntegerField(default=None)),
                ('isApproved', models.BooleanField(default=False)),
                ('isHighlighted', models.BooleanField(default=False)),
                ('isEdited', models.BooleanField(default=False)),
                ('isSpam', models.BooleanField(default=False)),
                ('isDeleted', models.BooleanField(default=False)),
                ('message', models.TextField(default=b'message', max_length=500)),
                ('forum', models.ForeignKey(to='subdapp.Forum')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(default=b'title', max_length=50)),
                ('slug', models.CharField(default=b'title', max_length=50)),
                ('message', models.CharField(default=b'message', max_length=150)),
                ('isClosed', models.BooleanField(default=False)),
                ('isDeleted', models.BooleanField(default=False)),
                ('forum', models.ForeignKey(to='subdapp.Forum')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'name', max_length=50)),
                ('username', models.CharField(default=b'username', max_length=50)),
                ('isAnonymous', models.BooleanField(default=False)),
                ('email', models.CharField(default=b'email', max_length=50)),
                ('about', models.CharField(default=b'about', max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='thread',
            name='user',
            field=models.ForeignKey(to='subdapp.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(to='subdapp.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(to='subdapp.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='forum',
            name='user',
            field=models.ForeignKey(to='subdapp.User'),
            preserve_default=True,
        ),
    ]
