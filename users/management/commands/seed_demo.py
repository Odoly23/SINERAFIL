"""Kria utilizadór demo (admin, mekániku, na'in) no dadus ezemplu kliente/servisu."""
import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from cliente.models import Kliente, Motor
from pesa.models import MovimentuStock, Pesa
from pesa.utils import register_movement
from servisu.models import Despeza, Servisu, ServisuPesa
from users.models import Emp
from users.utils import save_emp_account

PASSWORD = 'nerafil123'
FUNCIONARIU = [
    # naran, sexo, username, grupu, persen
    ('Admin Nerafil', 'Mane', 'admin', 'admin', 0),
    ('Zin', 'Mane', 'zin', 'mekaniku', 10),
    ('Anata', 'Mane', 'anata', 'mekaniku', 10),
    ('Abosa', 'Mane', 'abosa', 'mekaniku', 12),
    ("Na'in Ofisina", 'Mane', 'nain', 'nain', 0),
]
KLIENTE = [
    ('João Soares', '77231001'), ('Maria da Costa', '77231002'), ('Abel Guterres', '77231003'),
    ('Domingas Amaral', '77231004'), ('Paulo Ximenes', '77231005'), ('Luís Belo', '77231006'),
]
MOTOR = [('Honda', 'Beat'), ('Honda', 'Vario 125'), ('Yamaha', 'Vixion'), ('Honda', 'Supra X'),
         ('Yamaha', 'Mio'), ('Honda', 'Revo')]
KELUHAN = ['Troka oli no filtru', 'Troka kampas rem', 'Servisu CVT', 'Troka piston no ring',
           'Servisu kompletu', 'Troka busi no filtru udara']


class Command(BaseCommand):
    help = 'Kria dadus demo (password hotu-hotu: %s).' % PASSWORD

    @transaction.atomic
    def handle(self, *args, **opts):
        for name, sexo, username, group, pct in FUNCIONARIU:
            if User.objects.filter(username=username).exists():
                continue
            emp = Emp.objects.create(name=name, sexo=sexo, persen_ongkos=pct or 10)
            user = save_emp_account(emp, username, group, PASSWORD)
            if group == 'admin':
                user.is_superuser = user.is_staff = True
                user.save()

        if Servisu.objects.exists():
            self.stdout.write('Dadus servisu iha ona — la kria fali.')
            return

        rnd = random.Random(7)
        klientes = [Kliente.objects.create(name=n, phone=t, address='Dili') for n, t in KLIENTE]
        motors = [Motor.objects.create(kliente=k, plate='DIL-%04d' % (1000 + i), brand=MOTOR[i][0],
                                       model_name=MOTOR[i][1], year=2015 + i)
                  for i, k in enumerate(klientes)]
        pesa = list(Pesa.objects.filter(stock__gt=20, price_sell__lte=40))
        mekaniks = list(Emp.objects.filter(account__user__groups__name='mekaniku'))
        admin = User.objects.get(username='admin')
        today = timezone.localdate()
        for _ in range(24):
            i = rnd.randrange(len(klientes))
            m = rnd.choice(mekaniks)
            s = Servisu.objects.create(
                date=today - timedelta(days=rnd.randint(0, 150)), kliente=klientes[i], motor=motors[i],
                mekanik=m, complaint=rnd.choice(KELUHAN), labor_cost=rnd.choice([2, 3, 4.5, 5, 8, 12]),
                mech_percent=m.persen_ongkos,
                status=rnd.choice(['remata', 'remata', 'remata', 'prosesu', 'pendente']), created_by=admin)
            for p in (rnd.sample(pesa, k=min(len(pesa), rnd.randint(1, 3))) if pesa else []):
                qty = rnd.randint(1, 2)
                register_movement(p, MovimentuStock.SAI, qty, user=admin, servisu=s, reference=s.invoice_no,
                                  note='Uza iha servisu %s' % s.invoice_no)
                ServisuPesa.objects.create(servisu=s, pesa=p, quantity=qty,
                                           price_buy=p.price_buy, price_sell=p.price_sell)
        for d, v in [('Be, eletrisidade', 5), ('Ferramenta foun', 8), ('Hahan no be hemu', 4)]:
            Despeza.objects.create(description=d, amount=v, date=today - timedelta(days=rnd.randint(0, 40)),
                                   created_by=admin)
        if pesa:   # hodi hatudu alerta stock mínimu
            low = pesa[0]
            low.refresh_from_db()
            register_movement(low, MovimentuStock.SAI, low.stock - 1, user=admin, note='Demo alerta stock')
        self.stdout.write(self.style.SUCCESS(
            'Dadus demo kria ona. Login: admin / zin / anata / abosa / nain — password: %s' % PASSWORD))
