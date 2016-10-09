# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fb_id', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=50)),
                ('profile_url', models.URLField()),
                ('locale', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=10)),
                ('message', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fb_id', models.CharField(max_length=128)),
                ('email', models.CharField(max_length=50)),
                ('batch', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
