# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0014_user_thread'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_post_thread',
            name='user',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
