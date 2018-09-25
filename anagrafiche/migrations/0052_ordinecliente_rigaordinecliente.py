# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0051_auto_20150311_0053'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdineCliente',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('codice', models.CharField(max_length=9)),
                ('data', models.DateField()),
                ('cancellato', models.BooleanField(default=False)),
                ('cliente', models.ForeignKey(to='anagrafiche.Entita')),
                ('destinazione', models.ForeignKey(blank=True, to='anagrafiche.Indirizzo', null=True)),
            ],
            options={
                'verbose_name_plural': 'ordini clienti',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RigaOrdineCliente',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('quantita', models.IntegerField(verbose_name='quantità')),
                ('cancellato', models.BooleanField(default=False)),
                ('articolo', models.ForeignKey(to='anagrafiche.Articolo')),
                ('commessa', models.ForeignKey(to='anagrafiche.Commessa')),
                ('ordine', models.ForeignKey(related_name='righe', to='anagrafiche.OrdineCliente')),
                ('preventivo', models.ForeignKey(related_name='righe_ordine', to='anagrafiche.PreventivoCliente')),
            ],
            options={
                'verbose_name_plural': 'righe ordini clienti',
            },
            bases=(models.Model,),
        ),
    ]
