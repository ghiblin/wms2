# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0053_auto_20150311_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contatto',
            name='tipo',
            field=models.CharField(max_length=1, default='U', choices=[('U', 'Telefono ufficio'), ('A', 'Telefono abitazione'), ('C', 'Cellulare'), ('E', 'Email'), ('T', 'Email fatturazione'), ('F', 'Fax'), ('P', 'Personalizzato')]),
        ),
    ]
