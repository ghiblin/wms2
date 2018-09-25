# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0014_consuntivo_cancellato'),
    ]

    operations = [
        migrations.AddField(
            model_name='commessa',
            name='prodotto',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='consuntivo',
            name='ore',
            field=models.DecimalField(validators=[django.core.validators.MaxValueValidator(12), django.core.validators.MinValueValidator(0.5)], decimal_places=2, max_digits=5),
        ),
    ]
