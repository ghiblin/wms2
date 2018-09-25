# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0024_tipopagamento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='pagamento',
            field=models.ForeignKey(to='anagrafiche.TipoPagamento', default=1),
        ),
    ]
