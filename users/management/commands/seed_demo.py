"""Kria utilizadór demo (admin, mekániku, na'in) no dadus ezemplu kliente/ekipamentu/reparasaun."""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from customers.models import Customer, Equipment
from inventory.models import Part
from repairs.models import Repair
from repairs.utils import add_part
from users.models import User

PASSWORD = 'nerafil123'
USERS = [
    ('admin', 'Admin Nerafil', 'admin'),
    ('zin', 'Zin', 'technician'),
    ('anata', 'Anata', 'technician'),
    ('abosa', 'Abosa', 'technician'),
    ('nain', "Na'in Ofisina", 'owner'),
]
CUSTOMERS = [
    ('João Soares', '77231001'), ('Maria da Costa', '77231002'), ('Abel Guterres', '77231003'),
    ('Domingas Amaral', '77231004'), ('Paulo Ximenes', '77231005'), ('Luís Belo', '77231006'),
]
EQUIPMENT = [('Honda Beat', 'MH1JF8113KK'), ('Honda Vario 125', 'MH1JFM116LK'), ('Yamaha Vixion', 'MH3RG4210JK'),
             ('Honda Supra X', 'MH1KC4110HK'), ('Yamaha Mio', 'MH3SE8810GJ'), ('Honda Revo', 'MH1JB5110FK')]
DIAGNOSIS = ['Oli mesin no filtru oli presiza troka', 'Kampas rem kotuk aat tebes', 'Roller CVT no belt hotu ona',
             'Piston no ring aat, kompresaun fraku', 'Busi no filtru udara foer', 'Kabel rem sulin, presiza troka']


class Command(BaseCommand):
    help = 'Kria dadus demo (password hotu-hotu: %s).' % PASSWORD

    @transaction.atomic
    def handle(self, *args, **opts):
        for username, name, role in USERS:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username, PASSWORD, role=role, full_name=name)

        if Repair.objects.exists():
            self.stdout.write('Dadus reparasaun iha ona — la kria fali.')
            return

        rnd = random.Random(7)
        customers = [Customer.objects.create(name=n, phone=t) for n, t in CUSTOMERS]
        equipments = [Equipment.objects.create(customer=c, name=EQUIPMENT[i][0], serial_number=EQUIPMENT[i][1],
                                               plate='DIL-%04d' % (1000 + i))
                      for i, c in enumerate(customers)]
        parts = list(Part.objects.filter(stock__gte=20, selling_price__lte=40))
        technicians = list(User.objects.filter(role='technician'))
        now = timezone.now()

        flows = ['completed'] * 15 + ['in_progress'] * 3 + ['assigned'] * 2 + ['diagnosed'] * 2 + ['registered'] * 2
        for status in flows:
            i = rnd.randrange(len(customers))
            r = Repair.objects.create(customer=customers[i], equipment=equipments[i],
                                      created_at=now - timedelta(days=rnd.randint(0, 150)))
            if status == 'registered':
                continue
            r.diagnosis = rnd.choice(DIAGNOSIS)
            r.status = Repair.DIAGNOSED
            r.save()
            if status == 'diagnosed':
                continue
            r.technician = rnd.choice(technicians)
            r.status = Repair.ASSIGNED
            r.save()
            if status == 'assigned':
                continue
            for p in (rnd.sample(parts, k=min(len(parts), rnd.randint(1, 3))) if parts else []):
                add_part(r, p, rnd.randint(1, 2))
            r.status = Repair.IN_PROGRESS
            r.save()
            if status == 'in_progress':
                continue
            r.service_cost = rnd.choice([2, 3, 4.5, 5, 8, 12])
            r.status = Repair.COMPLETED
            r.save()
        if parts:   # hodi hatudu alerta stock mínimu
            low = Part.objects.get(pk=parts[0].pk)
            from inventory.utils import register_movement
            register_movement(low, 'out', low.stock - 1, note='Demo alerta stock')
        self.stdout.write(self.style.SUCCESS(
            'Dadus demo kria ona. Login: admin / zin / anata / abosa / nain — password: %s' % PASSWORD))
