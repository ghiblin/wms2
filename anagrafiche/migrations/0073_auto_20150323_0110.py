# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0072_auto_20150323_0103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contocorrente',
            name='swift',
            field=models.CharField(help_text='Chiamato anche codice BIC', null=True, max_length=11, blank=True),
        ),
    ]
