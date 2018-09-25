# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0054_auto_20150312_0848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indirizzo',
            name='tipo',
            field=models.CharField(max_length=1, choices=[('L', 'Sede legale'), ('O', 'Sede operativa'), ('A', 'Sede amministrativa'), ('C', 'Cantiere')], default='L'),
        ),
    ]
