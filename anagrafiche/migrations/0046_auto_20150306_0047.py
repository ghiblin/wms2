# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0045_preventivocliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preventivocliente',
            name='cliente',
            field=models.ForeignKey(to='anagrafiche.Entita'),
        ),
    ]
