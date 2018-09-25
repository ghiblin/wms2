# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0002_commessa'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dipendente',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('nome', models.CharField(max_length=20)),
                ('cognome', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name_plural': 'dipendenti',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='cliente',
            options={'verbose_name_plural': 'clienti'},
        ),
        migrations.AlterModelOptions(
            name='commessa',
            options={'verbose_name_plural': 'commesse'},
        ),
    ]
