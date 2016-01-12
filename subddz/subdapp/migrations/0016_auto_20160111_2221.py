# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0015_user_post_thread_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user_post_thread',
            old_name='user',
            new_name='post_id',
        ),
    ]
