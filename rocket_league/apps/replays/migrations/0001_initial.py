# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, null=True, blank=True)),
                ('slug', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player_name', models.CharField(max_length=100)),
                ('team', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Replay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'uploads/replay_files')),
                ('replay_id', models.CharField(max_length=100, null=True, blank=True)),
                ('player_name', models.CharField(max_length=100, null=True, blank=True)),
                ('server_name', models.CharField(max_length=100, null=True, blank=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('team_sizes', models.PositiveIntegerField(null=True, blank=True)),
                ('team_0_score', models.IntegerField(default=0, null=True, blank=True)),
                ('team_1_score', models.IntegerField(default=0, null=True, blank=True)),
                ('match_type', models.CharField(max_length=7, null=True, blank=True)),
                ('processed', models.BooleanField(default=False)),
                ('map', models.ForeignKey(blank=True, to='replays.Map', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='replay',
            field=models.ForeignKey(to='replays.Replay'),
        ),
        migrations.AddField(
            model_name='goal',
            name='player',
            field=models.ForeignKey(to='replays.Player'),
        ),
        migrations.AddField(
            model_name='goal',
            name='replay',
            field=models.ForeignKey(to='replays.Replay'),
        ),
    ]
