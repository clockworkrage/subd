# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0007_auto_20151114_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='parent',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
    ]
