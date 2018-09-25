# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0047_auto_20150306_0101'),
    ]

    operations = [
        migrations.RenameField(
            model_name='preventivocliente',
            old_name='aliquotaIVA',
            new_name='aliquota_IVA',
        ),
    ]
