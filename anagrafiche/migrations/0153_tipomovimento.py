# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0152_certificazioneferro'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoMovimento',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('descrizione', models.CharField(max_length=100)),
                ('segno', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name_plural': 'Tipi movimenti',
            },
        ),
    ]
