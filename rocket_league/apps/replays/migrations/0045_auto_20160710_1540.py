# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0044_auto_20160708_1328'),
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('type', models.CharField(default='body', choices=[('trail', 'Trail'), ('antenna', 'Antenna'), ('wheels', 'Wheels'), ('decal', 'Decal'), ('body', 'Body'), ('topper', 'Topper')], max_length=8)),
                ('internal_id', models.PositiveIntegerField()),
                ('name', models.CharField(default='Unknown', max_length=100)),
            ],
        ),
        migrations.DeleteModel(
            name='Body',
        ),
    ]
