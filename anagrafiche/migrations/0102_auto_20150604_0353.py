# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0101_auto_20150604_0313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articolo',
            name='unita_di_misura',
            field=models.CharField(max_length=2, choices=[('PZ', 'pz'), ('NR', 'n.'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l'), ('ML', 'ml')]),
        ),
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='articolo_unita_di_misura',
            field=models.CharField(default='NR', max_length=2, choices=[('PZ', 'pz'), ('NR', 'n.'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l'), ('ML', 'ml')]),
        ),
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='articolo_unita_di_misura',
            field=models.CharField(default='NR', max_length=2, choices=[('PZ', 'pz'), ('NR', 'n.'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l'), ('ML', 'ml')]),
        ),
    ]
