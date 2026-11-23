from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cliente.models import Kliente, Motor
from pesa.models import MovimentuStock, Pesa
from pesa.utils import StockError, register_movement
from servisu.models import Servisu
from users.models import Emp
from users.utils import save_emp_account


class BaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        def mk(username, group, pct=10):
            emp = Emp.objects.create(name=username.capitalize(), sexo='Mane', persen_ongkos=pct)
            return emp, save_emp_account(emp, username, group, 'x12345')
        cls.admin_emp, cls.admin = mk('adm', 'admin')
        cls.mek_emp, cls.mek = mk('mek', 'mekaniku')
        cls.mek2_emp, cls.mek2 = mk('mek2', 'mekaniku')
        cls.nain_emp, cls.nain = mk('own', 'nain')
        cls.pesa = Pesa.objects.create(code='P1', name='Piston X', price_buy=5, price_sell=12, stock_min=3)
        register_movement(cls.pesa, MovimentuStock.TAMA, 10)
        cls.kliente = Kliente.objects.create(name='Joao')
        cls.motor = Motor.objects.create(kliente=cls.kliente, plate='DIL-1', brand='Honda')
        cls.servisu = Servisu.objects.create(kliente=cls.kliente, motor=cls.motor, mekanik=cls.mek_emp,
                                             labor_cost=10, mech_percent=10)

    def login(self, user):
        self.client.force_login(user)


class StockTests(BaseCase):
    def test_sai_reduces_and_blocks(self):
        register_movement(self.pesa, MovimentuStock.SAI, 4)
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 6)
        with self.assertRaises(StockError):
            register_movement(self.pesa, MovimentuStock.SAI, 7)

    def test_add_part_reduces_stock_and_remove_restores(self):
        self.login(self.mek)
        r = self.client.post(reverse('servisu-pesa-add', args=[self.servisu.pk]),
                             {'pesa': self.pesa.pk, 'quantity': 3})
        self.assertEqual(r.status_code, 302)
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 7)
        self.servisu.refresh_from_db()
        self.assertEqual(self.servisu.total_parts, Decimal('36'))
        self.assertEqual(self.servisu.total, Decimal('46'))
        self.assertEqual(self.servisu.mech_fee, Decimal('1.00'))
        item = self.servisu.items.get()
        self.client.post(reverse('servisu-pesa-remove', args=[self.servisu.pk, item.pk]))
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 10)

    def test_cannot_use_more_than_stock(self):
        self.login(self.mek)
        self.client.post(reverse('servisu-pesa-add', args=[self.servisu.pk]),
                         {'pesa': self.pesa.pk, 'quantity': 99})
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 10)

    def test_delete_servisu_restores_stock(self):
        self.login(self.mek)
        self.client.post(reverse('servisu-pesa-add', args=[self.servisu.pk]), {'pesa': self.pesa.pk, 'quantity': 2})
        self.login(self.admin)
        self.client.post(reverse('servisu-delete', args=[self.servisu.pk]))
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 10)
        self.assertFalse(Servisu.objects.filter(pk=self.servisu.pk).exists())

    def test_manual_movimentu_form(self):
        self.login(self.admin)
        r = self.client.post(reverse('movimentu-add'), {
            'pesa': self.pesa.pk, 'tipu': 'sai', 'quantity': 4, 'price': '', 'date': '2026-05-01',
            'reference': 'tes', 'note': ''})
        self.assertEqual(r.status_code, 302)
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 6)


class RoleTests(BaseCase):
    def status(self, user, name, *args):
        self.login(user)
        return self.client.get(reverse(name, args=args)).status_code

    def test_public_pages(self):
        self.assertEqual(self.client.get(reverse('landing')).status_code, 200)
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('home')).status_code, 302)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)

    def test_login_flow(self):
        r = self.client.post(reverse('login'), {'username': 'adm', 'password': 'x12345'})
        self.assertRedirects(r, reverse('home'))
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.client.get(reverse('logout'))
        self.assertEqual(self.client.get(reverse('home')).status_code, 302)
        r = self.client.post(reverse('login'), {'username': 'adm', 'password': 'salah'})
        self.assertEqual(r.status_code, 200)

    def test_all_pages_for_admin(self):
        for name, args in [('home', []), ('dashboard', []), ('pesa-list', []), ('pesa-add', []),
                           ('pesa-detail', [self.pesa.pk]), ('pesa-edit', [self.pesa.pk]),
                           ('kategoria-list', []), ('kategoria-add', []), ('movimentu-list', []),
                           ('movimentu-add', []), ('kliente-list', []), ('kliente-add', []), ('motor-list', []),
                           ('motor-add', []), ('servisu-list', []), ('servisu-add', []),
                           ('servisu-detail', [self.servisu.pk]), ('servisu-edit', [self.servisu.pk]),
                           ('despeza-list', []), ('despeza-add', []), ('relatoriu', []), ('u-list', []),
                           ('user-add', []), ('emp-detail', [self.mek_emp.pk]), ('emp-update', [self.mek_emp.pk]),
                           ('UserProfile', []), ('change-password', []), ('nota-servisu', [self.servisu.pk])]:
            self.assertEqual(self.status(self.admin, name, *args), 200, name)

    def test_mekaniku_restrictions(self):
        for name in ['kategoria-list', 'movimentu-list', 'despeza-list', 'relatoriu', 'u-list', 'pesa-add']:
            self.assertEqual(self.status(self.mek, name), 403, name)
        for name in ['home', 'dashboard', 'pesa-list', 'servisu-list', 'kliente-list', 'servisu-add']:
            self.assertEqual(self.status(self.mek, name), 200, name)
        self.assertEqual(self.status(self.mek2, 'servisu-detail', self.servisu.pk), 403)
        self.assertEqual(self.status(self.mek2, 'nota-servisu', self.servisu.pk), 403)
        self.assertEqual(self.status(self.mek, 'nota-servisu', self.servisu.pk), 200)

    def test_nain_is_read_only(self):
        for name in ['dashboard', 'pesa-list', 'movimentu-list', 'despeza-list', 'relatoriu', 'servisu-list']:
            self.assertEqual(self.status(self.nain, name), 200, name)
        for name in ['pesa-add', 'servisu-add', 'u-list', 'movimentu-add', 'kliente-add']:
            self.assertEqual(self.status(self.nain, name), 403, name)
        self.login(self.nain)
        r = self.client.post(reverse('servisu-pesa-add', args=[self.servisu.pk]), {'pesa': self.pesa.pk, 'quantity': 1})
        self.assertEqual(r.status_code, 403)

    def test_mekaniku_cannot_edit_completed(self):
        self.servisu.status = Servisu.REMATA
        self.servisu.save()
        self.assertEqual(self.status(self.mek, 'servisu-edit', self.servisu.pk), 403)

    def test_superuser_without_group_is_admin(self):
        su = User.objects.create_superuser('root', 'r@x.com', 'x12345')
        self.assertEqual(self.status(su, 'u-list'), 200)


class UserTests(BaseCase):
    def test_create_emp_with_account(self):
        self.login(self.admin)
        r = self.client.post(reverse('user-add'), {
            'name': 'Dora Mekanik', 'sexo': 'Feto', 'phone': '', 'email': '', 'persen_ongkos': '12',
            'username': 'dora', 'group': 'mekaniku', 'password': 'abc12345', 'is_active': 'on'})
        self.assertEqual(r.status_code, 302, getattr(r, 'context', None) and r.context['form'].errors)
        u = User.objects.get(username='dora')
        self.assertTrue(u.check_password('abc12345'))
        self.assertEqual(u.groups.first().name, 'mekaniku')
        self.assertEqual(u.empuser.emp.persen_ongkos, Decimal('12'))

    def test_servisu_create_form_assigns_mekanik(self):
        self.login(self.mek)
        r = self.client.post(reverse('servisu-add'), {
            'date': '2026-05-01', 'kliente': self.kliente.pk, 'motor': self.motor.pk, 'complaint': 'oli',
            'labor_cost': '5', 'discount': '0', 'status': 'pendente', 'note': ''})
        self.assertEqual(r.status_code, 302, getattr(r, 'context', None) and r.context['form'].errors)
        s = Servisu.objects.latest('id')
        self.assertEqual(s.mekanik, self.mek_emp)
        self.assertEqual(s.mech_percent, Decimal('10'))
        self.assertTrue(s.invoice_no.startswith('SRV-202605-'))


class ReportTests(BaseCase):
    def test_pdfs(self):
        self.login(self.admin)
        for params in ['tipu=stock', 'tipu=movimentu&date_from=2020-01-01&date_to=2100-01-01',
                       'tipu=finanseiru&date_from=2020-01-01&date_to=2100-01-01']:
            r = self.client.get(reverse('relatoriu') + '?' + params)
            self.assertEqual(r['Content-Type'], 'application/pdf', params)
            self.assertTrue(r.content.startswith(b'%PDF'))
        r = self.client.get(reverse('nota-servisu', args=[self.servisu.pk]))
        self.assertTrue(r.content.startswith(b'%PDF'))


class KiosTests(BaseCase):
    def setUp(self):
        self.pesa.refresh_from_db()   # objek kelas bisa stale (stok diubah lewat register_movement)
        self.pesa.barcode = '8990000000012'
        self.pesa.save()
        self.pesa2 = Pesa.objects.create(code='P2', name='Busi Y', price_buy=1, price_sell=2.5, stock_min=1)
        register_movement(self.pesa2, MovimentuStock.TAMA, 5)

    def cart(self, *pairs):
        import json
        return json.dumps([{'pesa': p.pk, 'qty': q} for p, q in pairs])

    def checkout(self, cart, paid, discount='0', **extra):
        self.login(self.admin)
        return self.client.post(reverse('kios-checkout'), dict(cart=cart, paid=paid, discount=discount, **extra))

    def test_scan_by_barcode_and_code(self):
        self.login(self.admin)
        r = self.client.get(reverse('kios-scan'), {'q': '8990000000012'})
        self.assertEqual(r.json()['code'], 'P1')
        r = self.client.get(reverse('kios-scan'), {'q': 'p2'})
        self.assertEqual(r.json()['price'], '2.50')
        r = self.client.get(reverse('kios-scan'), {'q': 'tidak-ada'})
        self.assertEqual(r.status_code, 404)

    def test_cari_by_name(self):
        self.login(self.admin)
        r = self.client.get(reverse('kios-cari'), {'q': 'Busi'})
        self.assertEqual([x['code'] for x in r.json()['results']], ['P2'])

    def test_sale_change_and_stock(self):
        r = self.checkout(self.cart((self.pesa, 2), (self.pesa2, 1)), paid='30', discount='1.50')
        self.assertEqual(r.status_code, 200, r.content)
        data = r.json()
        # 2*12 + 2.5 = 26.5 - 1.5 = 25 ; bayar 30 -> kembali 5
        self.assertEqual(data['total'], '25.00')
        self.assertEqual(data['change'], '5.00')
        self.pesa.refresh_from_db(); self.pesa2.refresh_from_db()
        self.assertEqual((self.pesa.stock, self.pesa2.stock), (8, 4))
        from kios.models import Faan
        f = Faan.objects.get()
        self.assertTrue(f.invoice_no.startswith('KIO-'))
        self.assertEqual(f.profit, Decimal('2') * 7 + Decimal('1.5') - Decimal('1.5'))
        self.assertEqual(MovimentuStock.objects.filter(faan=f, tipu='sai').count(), 2)

    def test_insufficient_payment_rejected(self):
        r = self.checkout(self.cart((self.pesa, 1)), paid='10')
        self.assertEqual(r.status_code, 400)
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 10)

    def test_over_stock_rejected_atomic(self):
        r = self.checkout(self.cart((self.pesa2, 2), (self.pesa, 99)), paid='5000')
        self.assertEqual(r.status_code, 400)
        self.pesa2.refresh_from_db()
        self.assertEqual(self.pesa2.stock, 5)   # transaksi dibatalkan semua
        from kios.models import Faan
        self.assertEqual(Faan.objects.count(), 0)

    def test_server_uses_db_price_not_client(self):
        import json
        cart = json.dumps([{'pesa': self.pesa.pk, 'qty': 1, 'price': '0.01'}])
        r = self.checkout(cart, paid='5')
        self.assertEqual(r.status_code, 400)    # harga 12, bukan 0.01

    def test_void_restores_stock(self):
        self.checkout(self.cart((self.pesa, 3)), paid='36')
        from kios.models import Faan
        f = Faan.objects.get()
        self.pesa.refresh_from_db(); self.assertEqual(self.pesa.stock, 7)
        self.login(self.admin)
        self.client.post(reverse('faan-void', args=[f.pk]))
        self.pesa.refresh_from_db(); self.assertEqual(self.pesa.stock, 10)
        f.refresh_from_db(); self.assertEqual(f.status, 'anulada')
        self.client.post(reverse('faan-void', args=[f.pk]))   # anula dua kali -> tidak menambah stok lagi
        self.pesa.refresh_from_db(); self.assertEqual(self.pesa.stock, 10)

    def test_pages_and_documents(self):
        self.checkout(self.cart((self.pesa, 1)), paid='12')
        from kios.models import Faan
        f = Faan.objects.get()
        self.login(self.admin)
        for name, args in [('kios', []), ('faan-list', []), ('faan-detail', [f.pk]), ('faan-struk', [f.pk])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200, name)
        r = self.client.get(reverse('faan-pdf', args=[f.pk]))
        self.assertTrue(r.content.startswith(b'%PDF'))
        r = self.client.get(reverse('pesa-label'))
        self.assertTrue(r.content.startswith(b'%PDF'))
        r = self.client.get(reverse('pesa-label') + '?pk=%s&n=5' % self.pesa.pk)
        self.assertTrue(r.content.startswith(b'%PDF'))
        r = self.client.get(reverse('relatoriu') + '?tipu=finanseiru&date_from=2020-01-01&date_to=2100-01-01')
        self.assertTrue(r.content.startswith(b'%PDF'))

    def test_only_admin_can_use_kios(self):
        for user in (self.mek, self.nain):
            for name in ['kios', 'faan-list', 'kios-scan', 'kios-cari']:
                self.login(user)
                self.assertEqual(self.client.get(reverse(name)).status_code, 403, (user, name))
            r = self.client.post(reverse('kios-checkout'), {'cart': self.cart((self.pesa, 1)), 'paid': '50'})
            self.assertEqual(r.status_code, 403)
        self.pesa.refresh_from_db()
        self.assertEqual(self.pesa.stock, 10)

    def test_barcode_unique_and_optional(self):
        self.login(self.admin)
        base = {'code': 'N1', 'name': 'Baru', 'unit': 'pcs', 'price_buy': '1', 'price_sell': '2', 'stock_min': '1',
                'is_active': 'on', 'barcode': ''}
        r = self.client.post(reverse('pesa-add'), base)
        self.assertEqual(r.status_code, 302)
        r = self.client.post(reverse('pesa-add'), dict(base, code='N2', name='Baru2'))   # dua barcode kosong ok
        self.assertEqual(r.status_code, 302)
        r = self.client.post(reverse('pesa-add'), dict(base, code='N3', barcode='8990000000012'))
        self.assertEqual(r.status_code, 200)   # barcode duplikat ditolak
