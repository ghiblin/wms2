# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commessa',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('codice', models.CharField(max_length=20)),
                ('cliente', models.ForeignKey(to='anagrafiche.Cliente')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
