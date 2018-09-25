# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0067_auto_20150319_1047'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordinecliente',
            old_name='soggetto',
            new_name='oggetto',
        ),
    ]
