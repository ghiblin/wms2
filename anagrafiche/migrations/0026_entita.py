# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0025_auto_20150302_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entita',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('codice', models.CharField(max_length=30)),
                ('is_client', models.BooleanField(default=False)),
                ('is_supplier', models.BooleanField(default=False)),
                ('is_owner', models.BooleanField(default=False)),
                ('tipo', models.PositiveSmallIntegerField(choices=[(1, 'Persona fisica'), (2, 'Persona giuridica')], default=2)),
                ('nome', models.CharField(blank=True, null=True, max_length=40)),
                ('cognome', models.CharField(blank=True, null=True, max_length=40)),
                ('ragione_sociale', models.CharField(max_length=60)),
                ('codice_fiscale', models.CharField(blank=True, null=True, max_length=16)),
                ('partita_iva', models.CharField(blank=True, null=True, default='', max_length=12)),
                ('cancellato', models.BooleanField(default=False)),
                ('costo_riba', models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=4)),
                ('pagamento', models.ForeignKey(default=1, to='anagrafiche.TipoPagamento')),
            ],
            options={
                'verbose_name_plural': 'entità',
            },
            bases=(models.Model,),
        ),
    ]
