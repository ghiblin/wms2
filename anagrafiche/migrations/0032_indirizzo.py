# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0031_auto_20150302_1916'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indirizzo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(default='l', max_length=1, choices=[('l', 'Sede legale'), ('o', 'Sede operativa')])),
                ('via1', models.CharField(max_length=60)),
                ('via2', models.CharField(max_length=60, blank=True, null=True)),
                ('citta', models.CharField(max_length=40)),
                ('provincia', models.CharField(max_length=2)),
                ('cap', models.CharField(max_length=5)),
                ('nazione', models.CharField(max_length=30)),
                ('cancellato', models.BooleanField(default=False)),
                ('entita', models.ForeignKey(related_name='indirizzi', to='anagrafiche.Entita')),
            ],
            options={
                'verbose_name_plural': 'indirizzi',
            },
            bases=(models.Model,),
        ),
    ]
