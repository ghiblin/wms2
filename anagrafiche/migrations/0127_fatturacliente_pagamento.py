# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0126_auto_20151007_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatturacliente',
            name='pagamento',
            field=models.ForeignKey(default=1, to='anagrafiche.TipoPagamento'),
            preserve_default=True,
        ),
    ]
