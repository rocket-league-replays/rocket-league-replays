# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='replay',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AddField(
            model_name='map',
            name='image',
            field=models.FileField(null=True, upload_to=b'uploads/files', blank=True),
        ),
        migrations.AlterField(
            model_name='replay',
            name='replay_id',
            field=models.CharField(max_length=100, null=True, verbose_name=b'replay ID', blank=True),
        ),
    ]
