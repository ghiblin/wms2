# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0018_dipendente_matricola'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContoCorrente',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('preferita', models.BooleanField(default=False)),
                ('iban', models.CharField(max_length=30)),
                ('italiano', models.BooleanField(default=True)),
                ('intestatario', models.CharField(max_length=50)),
                ('nome_banca', models.CharField(max_length=30)),
                ('filiale', models.CharField(max_length=50, null=True, blank=True)),
                ('cancellato', models.BooleanField(default=False)),
                ('attivo', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(related_name='conti_correnti', to='anagrafiche.Cliente', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'conti correnti',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='banca',
            name='cliente',
        ),
        migrations.DeleteModel(
            name='Banca',
        ),
    ]
