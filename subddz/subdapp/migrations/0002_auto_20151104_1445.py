# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='message',
            field=models.TextField(default=b'message', max_length=500),
            preserve_default=True,
        ),
    ]
