# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0086_rigapreventivocliente_articolo_unita_di_misura'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigaordinecliente',
            name='articolo_unita_di_misura',
            field=models.CharField(choices=[('PZ', 'pz'), ('NR', 'nr'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l')], max_length=2, default='NR'),
            preserve_default=True,
        ),
    ]
