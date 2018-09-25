# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0003_auto_20150127_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consuntivo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('data', models.DateField()),
                ('ore', models.DecimalField(max_digits=5, decimal_places=2)),
                ('note', models.TextField(blank=True, null=True)),
                ('commessa', models.ForeignKey(to='anagrafiche.Commessa')),
                ('dipendente', models.ForeignKey(to='anagrafiche.Dipendente')),
            ],
            options={
                'verbose_name_plural': 'Consuntivi',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoLavoro',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('descrizione', models.CharField(unique=True, max_length=30)),
            ],
            options={
                'verbose_name_plural': 'Tipi lavoro',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='consuntivo',
            name='tipoLavoro',
            field=models.ForeignKey(to='anagrafiche.TipoLavoro'),
            preserve_default=True,
        ),
    ]
