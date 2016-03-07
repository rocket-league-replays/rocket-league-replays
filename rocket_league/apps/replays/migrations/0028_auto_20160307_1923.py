# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0027_auto_20160306_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='actor_id',
            field=models.PositiveIntegerField(null=True, blank=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='camera_settings',
            field=social.apps.django_app.default.fields.JSONField(null=True, blank=True, default='{}'),
        ),
        migrations.AddField(
            model_name='player',
            name='party_leader',
            field=models.ForeignKey(null=True, blank=True, to='replays.Player'),
        ),
        migrations.AddField(
            model_name='player',
            name='total_xp',
            field=models.PositiveIntegerField(null=True, blank=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='unique_id',
            field=models.CharField(null=True, max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(null=True, blank=True, choices=[(12, 'RankedSoloStandard'), (4, 'UnrankedChaos'), (1, 'UnrankedDuels'), (11, 'RankedDoubles'), (10, 'RankedDuels'), (3, 'UnrankedStandard'), (13, 'RankedStandard'), (2, 'UnrankedDoubles')], default=0),
        ),
    ]
