# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0009_user_post_forum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_post_forum',
            name='name',
        ),
    ]
