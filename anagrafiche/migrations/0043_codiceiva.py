# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0042_auto_20150305_1947'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodiceIVA',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('codice', models.CharField(blank=True, max_length=6, null=True)),
                ('descrizione', models.CharField(max_length=30)),
                ('percentuale', models.DecimalField(max_digits=4, decimal_places=2)),
            ],
            options={
                'verbose_name_plural': 'codici IVA',
            },
            bases=(models.Model,),
        ),
    ]
