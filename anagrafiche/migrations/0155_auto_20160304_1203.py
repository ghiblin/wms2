# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0154_articolo_giacenza'),
    ]

    operations = [
        migrations.CreateModel(
            name='Giacenza',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('quantita', models.DecimalField(verbose_name='quantità', max_digits=15, decimal_places=2)),
                ('note', models.CharField(max_length=500, blank=True, default='')),
            ],
            options={
                'verbose_name_plural': 'giacenze',
            },
        ),
        migrations.RenameField(
            model_name='articolo',
            old_name='giacenza',
            new_name='scorta',
        ),
        migrations.AddField(
            model_name='giacenza',
            name='articolo',
            field=models.ForeignKey(to='anagrafiche.Articolo'),
        ),
        migrations.AddField(
            model_name='giacenza',
            name='lotto',
            field=models.ForeignKey(to='anagrafiche.BollaFornitore', related_name='giacenze'),
        ),
    ]
