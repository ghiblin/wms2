# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0034_auto_20150303_0415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entita',
            name='tipo',
            field=models.CharField(max_length=1, choices=[('f', 'Persona fisica'), ('g', 'Persona giuridica')], default='g'),
        ),
    ]
