# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('anagrafiche', '0157_auto_20160304_1216'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movimento',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('quantita', models.DecimalField(verbose_name='quantità', decimal_places=2, max_digits=15)),
                ('unita_di_misura', models.CharField(max_length=20)),
                ('articolo', models.ForeignKey(related_name='movimenti', to='anagrafiche.Articolo')),
                ('autore', models.ForeignKey(related_name='movimenti', to=settings.AUTH_USER_MODEL)),
                ('destinazione', models.ForeignKey(related_name='movimenti', to='anagrafiche.Commessa')),
                ('lotto', models.ForeignKey(related_name='movimenti', to='anagrafiche.BollaFornitore')),
                ('tipo_movimento', models.ForeignKey(to='anagrafiche.TipoMovimento')),
            ],
            options={
                'verbose_name_plural': 'movimenti magazzino',
            },
        ),
    ]
