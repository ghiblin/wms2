# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0049_entita_straniero'),
    ]

    operations = [
        migrations.CreateModel(
            name='RigaPreventivoCliente',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('quantita', models.IntegerField(verbose_name='quantità')),
                ('cancellato', models.BooleanField(default=False)),
                ('articolo', models.ForeignKey(to='anagrafiche.Articolo')),
                ('commessa', models.ForeignKey(to='anagrafiche.Commessa')),
                ('preventivo', models.ForeignKey(related_name='righe', to='anagrafiche.PreventivoCliente')),
            ],
            options={
                'verbose_name_plural': 'righe preventivo clienti',
            },
            bases=(models.Model,),
        ),
    ]
