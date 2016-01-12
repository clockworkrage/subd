# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0016_auto_20160111_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_thread',
            name='count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
