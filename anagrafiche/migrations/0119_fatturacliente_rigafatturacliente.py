# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0118_auto_20150909_2218'),
    ]

    operations = [
        migrations.CreateModel(
            name='FatturaCliente',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('codice', models.CharField(max_length=9)),
                ('data', models.DateField()),
                ('note', models.TextField(blank=True, null=True)),
                ('cancellato', models.BooleanField(default=False)),
                ('aliquota_IVA', models.ForeignKey(blank=True, null=True, to='anagrafiche.AliquotaIVA')),
                ('cliente', models.ForeignKey(to='anagrafiche.Entita')),
                ('commessa', models.ForeignKey(to='anagrafiche.Commessa', related_name='fatture_clienti')),
            ],
            options={
                'verbose_name_plural': 'fatture clienti',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RigaFatturaCliente',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('articolo_descrizione', models.CharField(max_length=1000)),
                ('articolo_prezzo', models.DecimalField(decimal_places=2, max_digits=7)),
                ('articolo_unita_di_misura', models.CharField(default='NR', choices=[('PZ', 'pz'), ('NR', 'n.'), ('SC', 'sc'), ('ME', 'm'), ('M2', 'm²'), ('CM', 'cm'), ('MM', 'mm'), ('KG', 'kg'), ('HG', 'hg'), ('LI', 'l'), ('ML', 'ml')], max_length=2)),
                ('quantita', models.DecimalField(decimal_places=2, verbose_name='quantità', max_digits=8)),
                ('totale', models.DecimalField(decimal_places=2, max_digits=9)),
                ('note', models.CharField(blank=True, max_length=200, default='')),
                ('cancellato', models.BooleanField(default=False)),
                ('articolo', models.ForeignKey(to='anagrafiche.Articolo')),
                ('fattura', models.ForeignKey(to='anagrafiche.FatturaCliente', related_name='righe')),
                ('riga_ordine', models.OneToOneField(blank=True, null=True, to='anagrafiche.RigaOrdineCliente', related_name='riga_fattura')),
            ],
            options={
                'verbose_name_plural': 'righe fatture clienti',
            },
            bases=(models.Model,),
        ),
    ]
