# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0023_auto_20150224_1429'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoPagamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('descrizione', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name_plural': 'tipi pagamento',
            },
            bases=(models.Model,),
        ),
    ]
