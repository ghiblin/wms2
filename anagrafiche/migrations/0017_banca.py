# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0016_auto_20150223_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banca',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('preferita', models.BooleanField(default=False)),
                ('iban', models.CharField(max_length=30)),
                ('italiano', models.BooleanField(default=True)),
                ('intestatario', models.CharField(max_length=50)),
                ('nome_banca', models.CharField(max_length=30)),
                ('filiale', models.CharField(blank=True, max_length=50, null=True)),
                ('cancellato', models.BooleanField(default=False)),
                ('attivo', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(related_name='banche', to='anagrafiche.Cliente', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'banche',
            },
            bases=(models.Model,),
        ),
    ]
