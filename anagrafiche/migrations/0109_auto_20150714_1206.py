# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0108_aspettoesteriore_aspettoesterioremanager_causaletrasporto_causaletrasportomanager_porto_portomanager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bollacliente',
            name='aliquota_IVA',
        ),
        migrations.RemoveField(
            model_name='bollacliente',
            name='note',
        ),
        migrations.RemoveField(
            model_name='bollacliente',
            name='oggetto',
        ),
        migrations.RemoveField(
            model_name='bollacliente',
            name='pagamento',
        ),
        migrations.RemoveField(
            model_name='bollacliente',
            name='persona_di_riferimento',
        ),
        migrations.RemoveField(
            model_name='bollacliente',
            name='totale',
        ),
        migrations.AddField(
            model_name='bollacliente',
            name='aspetto_esteriore',
            field=models.ForeignKey(to='anagrafiche.AspettoEsteriore', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bollacliente',
            name='causale_trasporto',
            field=models.ForeignKey(to='anagrafiche.CausaleTrasporto', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bollacliente',
            name='porto',
            field=models.ForeignKey(to='anagrafiche.Porto', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bollacliente',
            name='trasporto_a_cura',
            field=models.ForeignKey(to='anagrafiche.TrasportoACura', null=True, blank=True),
            preserve_default=True,
        ),
    ]
