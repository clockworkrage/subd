# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0012_auto_20160111_2014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_post_forum',
            name='thread_id',
        ),
    ]
