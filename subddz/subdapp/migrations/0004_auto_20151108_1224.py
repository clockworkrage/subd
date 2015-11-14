# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0003_auto_20151108_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='thread',
            name='likes',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
