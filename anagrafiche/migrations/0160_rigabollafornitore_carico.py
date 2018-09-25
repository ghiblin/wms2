# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0159_movimento_cancellato'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigabollafornitore',
            name='carico',
            field=models.OneToOneField(blank=True, related_name='riga_bolla', null=True, to='anagrafiche.Movimento'),
        ),
    ]
