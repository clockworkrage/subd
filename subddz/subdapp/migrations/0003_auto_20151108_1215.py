# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0002_auto_20151104_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='dislikes',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='points',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='dislikes',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='points',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
