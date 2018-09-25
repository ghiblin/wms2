# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0105_auto_20150627_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='pagamento',
            field=models.ForeignKey(default=1, to='anagrafiche.TipoPagamento'),
            preserve_default=True,
        ),
    ]
