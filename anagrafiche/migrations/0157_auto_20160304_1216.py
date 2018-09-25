# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0156_auto_20160304_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giacenza',
            name='quantita',
            field=models.DecimalField(verbose_name='quantità', decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], max_digits=15),
        ),
    ]
