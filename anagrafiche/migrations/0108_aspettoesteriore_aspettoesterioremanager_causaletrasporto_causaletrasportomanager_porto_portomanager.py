# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0107_remove_rigabollacliente_commessa'),
    ]

    operations = [
        migrations.CreateModel(
            name='AspettoEsteriore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('descrizione', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'aspetti esteriori',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AspettoEsterioreManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CausaleTrasporto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('descrizione', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'causali trasporto',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CausaleTrasportoManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Porto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('descrizione', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'porto',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PortoManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrasportoACura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('descrizione', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'trasporto a cura',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrasportoACuraManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
