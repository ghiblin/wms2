# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0035_auto_20150303_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contatto',
            name='tipo',
            field=models.CharField(choices=[('U', 'Telefono ufficio'), ('A', 'Telefono abitazione'), ('C', 'Cellulare'), ('E', 'Email'), ('F', 'Fax'), ('P', 'Personalizzato')], max_length=1, default='U'),
        ),
        migrations.AlterField(
            model_name='entita',
            name='tipo',
            field=models.CharField(choices=[('F', 'Persona fisica'), ('G', 'Persona giuridica')], max_length=1, default='G'),
        ),
        migrations.AlterField(
            model_name='indirizzo',
            name='tipo',
            field=models.CharField(choices=[('L', 'Sede legale'), ('O', 'Sede operativa')], max_length=1, default='L'),
        ),
    ]
