# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0103_preventivocliente_commessa'),
    ]

    operations = [
        migrations.CreateModel(
            name='BollaCliente',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('codice', models.CharField(max_length=9)),
                ('data', models.DateField()),
                ('oggetto', models.CharField(max_length=100, blank=True, null=True)),
                ('totale', models.DecimalField(max_digits=9, default=0, decimal_places=2)),
                ('note', models.TextField(blank=True, null=True)),
                ('cancellato', models.BooleanField(default=False)),
                ('aliquota_IVA', models.ForeignKey(to='anagrafiche.AliquotaIVA', blank=True, null=True)),
                ('cliente', models.ForeignKey(to='anagrafiche.Entita')),
                ('commessa', models.ForeignKey(to='anagrafiche.Commessa', related_name='bolle_clienti')),
                ('destinazione', models.ForeignKey(to='anagrafiche.Indirizzo', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'bolle clienti',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RigaBollaCliente',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('articolo_descrizione', models.CharField(max_length=1000)),
                ('articolo_prezzo', models.DecimalField(max_digits=7, decimal_places=2)),
                ('articolo_unita_di_misura', models.CharField(max_length=2, default='NR', choices=[('PZ', 'pz'), ('NR', 'n.'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l'), ('ML', 'ml')])),
                ('quantita', models.DecimalField(max_digits=8, verbose_name='quantità', decimal_places=2)),
                ('totale', models.DecimalField(max_digits=9, decimal_places=2)),
                ('note', models.CharField(max_length=200, default='', blank=True)),
                ('cancellato', models.BooleanField(default=False)),
                ('articolo', models.ForeignKey(to='anagrafiche.Articolo')),
                ('bolla', models.ForeignKey(to='anagrafiche.BollaCliente', related_name='righe')),
                ('commessa', models.ForeignKey(to='anagrafiche.Commessa', blank=True, null=True)),
                ('riga_ordine', models.OneToOneField(to='anagrafiche.RigaOrdineCliente', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'righe bolle clienti',
            },
            bases=(models.Model,),
        ),
    ]
