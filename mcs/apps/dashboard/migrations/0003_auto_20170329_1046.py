# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 10:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20170329_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cloudring',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='file',
            name='owner',
        ),
    ]