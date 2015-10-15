# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subdapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='about',
            field=models.TextField(default=b'about', max_length=700),
            preserve_default=True,
        ),
    ]
