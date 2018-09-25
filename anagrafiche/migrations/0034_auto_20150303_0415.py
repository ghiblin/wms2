# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0033_contatto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contatto',
            name='custom_label',
            field=models.CharField(null=True, blank=True, help_text='Etichetta da usare se tipo contatto = personalizzato', max_length=30),
        ),
    ]
