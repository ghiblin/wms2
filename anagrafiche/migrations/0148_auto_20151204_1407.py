# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0147_preventivofornitore_totale_su_stampa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='classe_di_esecuzione',
        ),
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='disegni_costruttivi',
        ),
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='relazione_di_calcolo',
        ),
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='spessori',
        ),
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='tipo_di_acciaio',
        ),
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='verniciatura',
        ),
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='wps',
        ),
        migrations.RemoveField(
            model_name='ordinefornitore',
            name='zincatura',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='classe_di_esecuzione',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='disegni_costruttivi',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='relazione_di_calcolo',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='spessori',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='tipo_di_acciaio',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='verniciatura',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='wps',
        ),
        migrations.RemoveField(
            model_name='preventivofornitore',
            name='zincatura',
        ),
    ]
