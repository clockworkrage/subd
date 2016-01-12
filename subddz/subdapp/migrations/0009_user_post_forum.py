# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0008_auto_20151213_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Post_Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True)),
                ('short_name', models.CharField(default=b'shortforumname', max_length=50)),
                ('thread_id', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to='subdapp.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
