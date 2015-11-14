# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0004_auto_20151108_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thread',
            name='date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
