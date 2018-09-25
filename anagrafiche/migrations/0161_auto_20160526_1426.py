# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0160_rigabollafornitore_carico'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigafatturafornitore',
            name='articolo_prezzo',
            field=models.DecimalField(max_digits=16, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='rigaordinefornitore',
            name='articolo_prezzo',
            field=models.DecimalField(max_digits=16, decimal_places=5),
        ),
    ]
