# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0145_auto_20151127_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bollafornitore',
            name='peso_lordo',
            field=models.CharField(max_length=50, blank=True, default='0', null=True),
        ),
        migrations.AlterField(
            model_name='bollafornitore',
            name='peso_netto',
            field=models.CharField(max_length=50, blank=True, default='0', null=True),
        ),
    ]
