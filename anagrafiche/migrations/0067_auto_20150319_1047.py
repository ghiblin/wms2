# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0066_auto_20150318_0254'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordinecliente',
            old_name='descrizione',
            new_name='soggetto',
        ),
    ]
