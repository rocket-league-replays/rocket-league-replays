# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site', '0005_auto_20160319_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patron',
            name='patron_id',
            field=models.PositiveIntegerField(verbose_name=b'Patron ID'),
        ),
        migrations.AlterField(
            model_name='patron',
            name='pledge_amount',
            field=models.PositiveIntegerField(help_text=b'Amount pledged (in cents)'),
        ),
        migrations.AlterField(
            model_name='patron',
            name='pledge_id',
            field=models.PositiveIntegerField(verbose_name=b'Pledge ID'),
        ),
    ]
