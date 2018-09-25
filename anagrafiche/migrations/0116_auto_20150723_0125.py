# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0115_auto_20150717_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rigabollacliente',
            name='articolo_prezzo',
        ),
        migrations.RemoveField(
            model_name='rigabollacliente',
            name='totale',
        ),
    ]
