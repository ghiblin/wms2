# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0037_classearticolo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Articolo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('codice', models.CharField(max_length=6)),
                ('descrizione', models.CharField(max_length=50)),
                ('codice_fornitore', models.CharField(help_text='Codice usato dal fornitore per identificare questo articolo', blank=True, null=True, max_length=50)),
                ('note', models.TextField(blank=True, null=True)),
                ('unita_di_misura', models.CharField(choices=[('ME', 'metri'), ('CM', 'centimetri'), ('KG', 'chili'), ('HG', 'etti'), ('LI', 'litri'), ('SC', 'scatole')], max_length=1)),
                ('prezzo_di_listino', models.DecimalField(decimal_places=2, max_digits=7)),
                ('classe', models.ForeignKey(to='anagrafiche.ClasseArticolo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
