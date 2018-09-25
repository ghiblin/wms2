# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0155_auto_20160304_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giacenza',
            name='quantita',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(Decimal('0'))], decimal_places=2, verbose_name='quantità', max_digits=15),
        ),
    ]
