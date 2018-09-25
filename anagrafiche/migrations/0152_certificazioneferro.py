# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0151_bollafornitore_classe_di_corrosivita'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificazioneFerro',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('descrizione', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Certificazioni ferro',
            },
        ),
    ]
