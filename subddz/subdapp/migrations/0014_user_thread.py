# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0013_remove_user_post_forum_thread_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=50, null=True)),
                ('short_name', models.CharField(default=b'shortforumname', max_length=50)),
                ('thread_id', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
