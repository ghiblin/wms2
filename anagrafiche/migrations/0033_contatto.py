# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0032_indirizzo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contatto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('tipo', models.CharField(default='u', choices=[('u', 'Telefono ufficio'), ('a', 'Telefono abitazione'), ('c', 'Cellulare'), ('e', 'Email'), ('f', 'Fax'), ('p', 'Personalizzato')], max_length=1)),
                ('valore', models.CharField(max_length=60)),
                ('custom_label', models.CharField(help_text='Etichetta da usare se tipo contatto = personalizzato', max_length=30)),
                ('note', models.TextField(blank=True, null=True)),
                ('cancellato', models.BooleanField(default=False)),
                ('entita', models.ForeignKey(to='anagrafiche.Entita', related_name='contatti')),
            ],
            options={
                'verbose_name_plural': 'contatti',
            },
            bases=(models.Model,),
        ),
    ]
