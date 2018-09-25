# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0158_movimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimento',
            name='cancellato',
            field=models.BooleanField(default=False),
        ),
    ]
