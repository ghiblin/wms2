# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0161_auto_20160526_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indirizzo',
            name='tipo',
            field=models.CharField(max_length=1, choices=[('L', 'Sede legale'), ('O', 'Sede operativa'), ('A', 'Sede amministrativa'), ('C', 'Cantiere'), ('X', 'Sede cliente')], default='L'),
        ),
    ]
