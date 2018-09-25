# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0122_auto_20150914_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigafatturacliente',
            name='riga_bolla',
            field=models.OneToOneField(null=True, related_name='riga_fattura', blank=True, to='anagrafiche.RigaBollaCliente'),
            preserve_default=True,
        ),
    ]
