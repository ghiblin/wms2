# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0063_rigaordinecliente_totale'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='pagamento',
        ),
        migrations.DeleteModel(
            name='Cliente',
        ),
    ]
