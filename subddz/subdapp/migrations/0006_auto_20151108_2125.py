# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0005_auto_20151108_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='follow',
            field=models.ManyToManyField(to='subdapp.User'),
            preserve_default=True,
        ),
    ]
