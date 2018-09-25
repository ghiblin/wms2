# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0030_auto_20150302_1736'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tipopagamento',
            options={'verbose_name_plural': 'tipi pagamento', 'ordering': ('id',)},
        ),
    ]
