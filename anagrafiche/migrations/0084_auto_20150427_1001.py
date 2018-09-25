# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0083_auto_20150409_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='pagamento',
            field=models.ForeignKey(default=1, to='anagrafiche.TipoPagamento'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='pagamento',
            field=models.ForeignKey(default=1, to='anagrafiche.TipoPagamento'),
            preserve_default=True,
        ),
    ]
