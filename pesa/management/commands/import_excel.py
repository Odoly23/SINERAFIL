"""Impor dadus pesa-rezerva husi Excel nota supplier (sheet 'Sparpart-motor', kolum A–G)."""
import re
from decimal import Decimal
from pathlib import Path

import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from custom.models import Kategoria
from pesa.models import MovimentuStock, Pesa
from pesa.utils import register_movement

CATEGORIES = [
    ('PISTON', 'Piston & Ring'), ('RING', 'Piston & Ring'),
    ('SHOCK', 'Suspensaun'), ('AS SHOCK', 'Suspensaun'),
    ('BEARING', 'Laher / Bearing'), ('LAHER', 'Laher / Bearing'),
    ('KAMPAS', 'Rem & Kampas'), ('MASTER REM', 'Rem & Kampas'), ('KABEL', 'Kabel'),
    ('FILTER', 'Filtru'), ('BUSI', 'Eletriku'), ('CDI', 'Eletriku'), ('KOIL', 'Eletriku'),
    ('REGULATOR', 'Eletriku'), ('BOHLAM', 'Eletriku'), ('LAMPU', 'Eletriku'),
    ('KUNCI', 'Eletriku'), ('SEKRING', 'Eletriku'),
    ('ROLLER', 'Transmisaun CVT'), ('ROTAK', 'Transmisaun CVT'), ('GIR', 'Transmisaun CVT'),
    ('GEAR', 'Transmisaun CVT'), ('KIPROK', 'Transmisaun CVT'), ('NOKEN', 'Mesin'),
    ('KARET', 'Karet & Seal'), ('SEAL', 'Karet & Seal'), ('OLI', 'Oli & Lubrikante'),
]


def guess_category(name):
    up = name.upper()
    for key, cat in CATEGORIES:
        if re.search(r'\b%s\b' % re.escape(key), up):
            return cat
    return 'Seluruh'


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Command(BaseCommand):
    help = 'Impor pesa-rezerva husi file Excel (data/NOTA_DAVID_TILES-II.xlsx).'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', default=str(settings.BASE_DIR / 'data' / 'NOTA_DAVID_TILES-II.xlsx'))
        parser.add_argument('--sheet', default='Sparpart-motor')
        parser.add_argument('--kurs', type=float, default=settings.KURS_RUPIAH_PER_USD,
                            help='Kursu Rupiah per 1 USD (default %s)' % settings.KURS_RUPIAH_PER_USD)

    @transaction.atomic
    def handle(self, path, sheet, kurs, **opts):
        if not Path(path).exists():
            raise CommandError('File la hetan: %s' % path)
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        if sheet not in wb.sheetnames:
            raise CommandError('Sheet "%s" la hetan. Sheet sira: %s' % (sheet, ', '.join(wb.sheetnames)))
        created = skipped = 0
        counter = Pesa.objects.count()
        for row in wb[sheet].iter_rows(min_row=1, max_col=7, values_only=True):
            _, name, qty, harga_rp, _, harga_jual, _ = (list(row) + [None] * 7)[:7]
            if not isinstance(name, str) or not name.strip() or name.strip().upper() in ('NAMA BARANG', 'NO'):
                continue
            if not (num(qty) and num(harga_rp) and num(harga_jual)) or qty <= 0:
                continue
            name = ' '.join(name.split())
            if Pesa.objects.filter(name__iexact=name).exists():
                skipped += 1
                continue
            counter += 1
            sosa = (Decimal(str(harga_rp)) / Decimal(str(kurs))).quantize(Decimal('0.01'))
            faan = Decimal(str(harga_jual)).quantize(Decimal('0.01'))
            if faan <= 0:  # harga jual la iha iha Excel -> margem 30%
                faan = (sosa * Decimal('1.3')).quantize(Decimal('0.01'))
            cat, _ = Kategoria.objects.get_or_create(name=guess_category(name))
            pesa = Pesa.objects.create(
                code='PSA-%04d' % counter, name=name, kategoria=cat,
                price_buy=sosa, price_sell=faan,
                stock_min=1 if qty <= 4 else 3)
            register_movement(pesa, MovimentuStock.TAMA, int(qty), reference='Nota David',
                              note='Stock inisiál husi Excel')
            created += 1
        self.stdout.write(self.style.SUCCESS(
            'Pesa foun: %d · la tama (iha ona): %d · kursu 1 USD = Rp %s' % (created, skipped, kurs)))
