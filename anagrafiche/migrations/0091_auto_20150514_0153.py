# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0090_auto_20150511_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventivocliente',
            name='disegni_costruttivi',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='relazione_di_calcolo',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
