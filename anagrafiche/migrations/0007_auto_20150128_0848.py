# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0006_dipendente_costo_orario'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cliente',
            old_name='ragioneSociale',
            new_name='ragione_sociale',
        ),
        migrations.RenameField(
            model_name='consuntivo',
            old_name='tipoLavoro',
            new_name='tipo_lavoro',
        ),
    ]
