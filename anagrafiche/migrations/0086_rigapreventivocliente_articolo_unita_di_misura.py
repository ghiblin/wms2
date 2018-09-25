# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0085_entita_persona_di_riferimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigapreventivocliente',
            name='articolo_unita_di_misura',
            field=models.CharField(choices=[('PZ', 'pz'), ('NR', 'nr'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l')], max_length=2, default='NR'),
            preserve_default=True,
        ),
    ]
