# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0039_articolo_cancellato'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articolo',
            options={'verbose_name_plural': 'articoli'},
        ),
        migrations.AlterField(
            model_name='articolo',
            name='unita_di_misura',
            field=models.CharField(choices=[('ME', 'metri'), ('CM', 'centimetri'), ('KG', 'chili'), ('HG', 'etti'), ('LI', 'litri'), ('SC', 'scatole')], max_length=2),
        ),
    ]
