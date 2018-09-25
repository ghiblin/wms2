# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0044_auto_20150306_0007'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreventivoCliente',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('codice', models.CharField(max_length=8)),
                ('data', models.DateField()),
                ('oggetto', models.CharField(blank=True, max_length=100, null=True)),
                ('accettato', models.BooleanField(default=False)),
                ('note', models.TextField(blank=True, null=True)),
                ('cancellato', models.BooleanField(default=False)),
                ('aliquotaIVA', models.ForeignKey(blank=True, null=True, to='anagrafiche.AliquotaIVA')),
                ('cliente', models.ForeignKey(to='anagrafiche.Cliente')),
                ('destinazione', models.ForeignKey(blank=True, null=True, to='anagrafiche.Indirizzo')),
            ],
            options={
                'verbose_name_plural': 'preventivi clienti',
            },
            bases=(models.Model,),
        ),
    ]
