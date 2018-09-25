# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0106_bollacliente_pagamento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rigabollacliente',
            name='commessa',
        ),
    ]
