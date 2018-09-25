# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0022_auto_20150224_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='pagamento',
            field=models.IntegerField(default=1, choices=[(1, 'Rimessa Diretta Vista Fattura'), (2, 'Bonifico Bancario Vista Fattura'), (3, 'Bonifico Bancario 30gg d.f.'), (4, 'Bonifico Bancario 30/60/90/120gg d.f. f.m.'), (5, 'Bonifico Bancario 120/150gg d.f. f.m.'), (6, 'Ri.ba. 30gg d.f. f.m.'), (7, 'Ri.ba. 30/60gg d.f. f.m.'), (8, 'Ri.ba. 60gg d.f. f.m.'), (9, 'Ri.ba. 60/90 gg d.f. f.m.'), (10, 'Ri.ba. 60/90gg + 10gg d.f. f.m.'), (11, 'Ri.ba 60gg f.m. + 15gg')]),
        ),
    ]
