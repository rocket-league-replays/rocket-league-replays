# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site', '0004_standardpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patron',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('pledge_id', models.PositiveIntegerField()),
                ('pledge_amount', models.PositiveIntegerField()),
                ('pledge_created', models.DateTimeField()),
                ('pledge_declined_since', models.DateTimeField(null=True, blank=True)),
                ('patron_id', models.PositiveIntegerField()),
                ('patron_email', models.EmailField(max_length=254)),
                ('patron_facebook', models.CharField(null=True, blank=True, max_length=300)),
                ('patron_twitter', models.CharField(null=True, blank=True, max_length=300)),
                ('patron_youtube', models.CharField(null=True, blank=True, max_length=300)),
            ],
        ),
        migrations.AlterField(
            model_name='contentcolumn',
            name='url',
            field=models.CharField(verbose_name='URL', max_length=100),
        ),
    ]
