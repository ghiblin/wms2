# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0091_auto_20150514_0153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='articolo_descrizione',
            field=models.CharField(max_length=1000),
        ),
    ]
