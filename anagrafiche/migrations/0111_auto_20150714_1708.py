# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0110_auto_20150714_1443'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AspettoEsteriore',
            new_name='TipoAspettoEsteriore',
        ),
        migrations.RenameModel(
            old_name='AspettoEsterioreManager',
            new_name='TipoAspettoEsterioreManager',
        ),
        migrations.RenameModel(
            old_name='CausaleTrasporto',
            new_name='TipoCausaleTrasporto',
        ),
        migrations.RenameModel(
            old_name='CausaleTrasportoManager',
            new_name='TipoCausaleTrasportoManager',
        ),
        migrations.RenameModel(
            old_name='Porto',
            new_name='TipoPorto',
        ),
        migrations.RenameModel(
            old_name='PortoManager',
            new_name='TipoPortoManager',
        ),
        migrations.RenameModel(
            old_name='TrasportoACura',
            new_name='TipoTrasportoACura',
        ),
        migrations.RenameModel(
            old_name='TrasportoACuraManager',
            new_name='TipoTrasportoACuraManager',
        ),
        migrations.AlterModelOptions(
            name='tipoaspettoesteriore',
            options={'verbose_name_plural': 'tipi aspetto esteriore'},
        ),
        migrations.AlterModelOptions(
            name='tipocausaletrasporto',
            options={'verbose_name_plural': 'tipi causali trasporto'},
        ),
        migrations.AlterModelOptions(
            name='tipoporto',
            options={'verbose_name_plural': 'tipi porto'},
        ),
        migrations.AlterModelOptions(
            name='tipotrasportoacura',
            options={'verbose_name_plural': 'tipi trasporto a cura'},
        ),
    ]
