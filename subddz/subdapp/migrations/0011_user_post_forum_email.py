# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0010_remove_user_post_forum_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_post_forum',
            name='email',
            field=models.CharField(max_length=50, null=True),
            preserve_default=True,
        ),
    ]
