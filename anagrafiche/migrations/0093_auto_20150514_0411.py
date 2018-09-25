# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0092_auto_20150514_0410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='articolo_descrizione',
            field=models.CharField(max_length=1000),
        ),
    ]
