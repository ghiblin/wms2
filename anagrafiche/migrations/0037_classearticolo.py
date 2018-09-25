# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0036_auto_20150303_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClasseArticolo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('sigla', models.CharField(max_length=2)),
                ('descrizione', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'classi articoli',
            },
            bases=(models.Model,),
        ),
    ]
