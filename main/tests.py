from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from customers.models import Customer, Equipment
from inventory.models import Part, StockMovement
from inventory.utils import StockError, register_movement
from repairs.models import Repair
from users.models import ActivityLog, User


class BaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('adm', 'x12345', role='admin', full_name='Admin')
        cls.tech = User.objects.create_user('tek', 'x12345', role='technician', full_name='Teknik 1')
        cls.tech2 = User.objects.create_user('tek2', 'x12345', role='technician')
        cls.owner = User.objects.create_user('own', 'x12345', role='owner')
        cls.part = Part.objects.create(sku='P1', name='Piston X', purchase_price=5, selling_price=12, minimum_stock=3)
        register_movement(cls.part, StockMovement.IN, 10)
        cls.customer = Customer.objects.create(name='Joao', phone='7700')
        cls.equipment = Equipment.objects.create(customer=cls.customer, name='Honda Beat', plate='DIL-1',
                                                 serial_number='MH123')

    def login(self, user):
        self.client.force_login(user)

    def new_repair(self, status=Repair.REGISTERED, technician=None, diagnosis=''):
        return Repair.objects.create(customer=self.customer, equipment=self.equipment, status=status,
                                     technician=technician, diagnosis=diagnosis)


class SchemaTests(TestCase):
    """Skema database tuir ERD dosen: naran tabel no kolun."""

    def cols(self, model):
        return {f.column for f in model._meta.concrete_fields}

    def test_tables_and_columns_follow_erd(self):
        from custom.models import Category, Supplier
        from repairs.models import RepairPart
        erd = {
            User: ('user', {'id', 'username', 'password', 'role'}),
            Customer: ('customer', {'id', 'name', 'phone'}),
            Equipment: ('equipment', {'id', 'customer_id', 'name', 'serial_number'}),
            Category: ('category', {'id', 'name'}),
            Supplier: ('supplier', {'id', 'name', 'phone'}),
            Part: ('part', {'id', 'sku', 'name', 'category_id', 'supplier_id', 'stock', 'minimum_stock', 'purchase_price'}),
            Repair: ('repair', {'id', 'repair_number', 'customer_id', 'equipment_id', 'technician_id', 'status', 'service_cost'}),
            RepairPart: ('repair_part', {'id', 'repair_id', 'part_id', 'quantity', 'unit_price'}),
            StockMovement: ('stock_movement', {'id', 'part_id', 'movement_type', 'quantity', 'created_at'}),
            ActivityLog: ('activity_log', {'id', 'user_id', 'action', 'created_at'}),
        }
        extras = {User: {'full_name', 'is_active'}, Equipment: {'plate'}, Part: {'selling_price'},
                  Repair: {'diagnosis', 'created_at'}, StockMovement: {'note'}}
        for model, (table, columns) in erd.items():
            self.assertEqual(model._meta.db_table, table)
            self.assertEqual(self.cols(model), columns | extras.get(model, set()), table)


class WorkflowTests(BaseCase):
    def test_full_flow_matches_flowchart(self):
        # 1 Register New Repair (admin)
        self.login(self.admin)
        r = self.client.post(reverse('repair-add'), {'customer': self.customer.pk, 'equipment': self.equipment.pk})
        self.assertEqual(r.status_code, 302)
        rep = Repair.objects.get()
        self.assertTrue(rep.repair_number.startswith('RPR-'))
        self.assertEqual(rep.status, Repair.REGISTERED)
        # urutan dijaga: belum boleh assign / pakai part / start / complete
        self.client.post(reverse('repair-start', args=[rep.pk]))
        self.client.post(reverse('repair-part-add', args=[rep.pk]), {'part': self.part.pk, 'quantity': 1})
        self.client.post(reverse('repair-assign', args=[rep.pk]), {'technician': self.tech.pk})
        rep.refresh_from_db()
        self.assertEqual((rep.status, rep.technician), (Repair.REGISTERED, None))
        # 2 Damage Diagnosis
        self.client.post(reverse('repair-diagnose', args=[rep.pk]), {'diagnosis': 'Piston aat'})
        rep.refresh_from_db(); self.assertEqual(rep.status, Repair.DIAGNOSED)
        # 3 Assign Technician
        self.client.post(reverse('repair-assign', args=[rep.pk]), {'technician': self.tech.pk})
        rep.refresh_from_db(); self.assertEqual((rep.status, rep.technician), (Repair.ASSIGNED, self.tech))
        # 4 Spare Parts Usage + Automatic Stock Update (teknisi yang ditugaskan)
        self.login(self.tech)
        self.client.post(reverse('repair-part-add', args=[rep.pk]), {'part': self.part.pk, 'quantity': 3})
        self.part.refresh_from_db(); self.assertEqual(self.part.stock, 7)
        item = rep.parts.get()
        self.assertEqual(item.unit_price, Decimal('12.00'))      # default = selling_price
        self.assertTrue(StockMovement.objects.filter(part=self.part, movement_type='out', quantity=3).exists())
        # 5 Repair Process
        self.client.post(reverse('repair-start', args=[rep.pk]))
        rep.refresh_from_db(); self.assertEqual(rep.status, Repair.IN_PROGRESS)
        # 6 Confirm Completion
        r = self.client.post(reverse('repair-complete', args=[rep.pk]), {'service_cost': '10'})
        rep.refresh_from_db()
        self.assertEqual(rep.status, Repair.COMPLETED)
        self.assertEqual(rep.total, Decimal('46.00'))            # 3*12 + 10
        self.assertEqual(rep.profit, Decimal('10') + Decimal('3') * 7)
        # selesai -> terkunci
        self.client.post(reverse('repair-part-add', args=[rep.pk]), {'part': self.part.pk, 'quantity': 1})
        self.part.refresh_from_db(); self.assertEqual(self.part.stock, 7)
        self.assertEqual(self.client.get(reverse('repair-diagnose', args=[rep.pk])).status_code, 403)

    def test_remove_part_and_delete_restore_stock(self):
        rep = self.new_repair(Repair.ASSIGNED, self.tech, 'x')
        self.login(self.tech)
        self.client.post(reverse('repair-part-add', args=[rep.pk]), {'part': self.part.pk, 'quantity': 4, 'unit_price': '15'})
        self.part.refresh_from_db(); self.assertEqual(self.part.stock, 6)
        self.assertEqual(rep.parts.get().unit_price, Decimal('15.00'))
        item = rep.parts.get()
        self.client.post(reverse('repair-part-remove', args=[rep.pk, item.pk]))
        self.part.refresh_from_db(); self.assertEqual(self.part.stock, 10)
        self.client.post(reverse('repair-part-add', args=[rep.pk]), {'part': self.part.pk, 'quantity': 2})
        self.login(self.admin)
        self.client.post(reverse('repair-delete', args=[rep.pk]))
        self.part.refresh_from_db(); self.assertEqual(self.part.stock, 10)
        self.assertFalse(Repair.objects.filter(pk=rep.pk).exists())

    def test_cannot_use_more_than_stock(self):
        rep = self.new_repair(Repair.IN_PROGRESS, self.tech, 'x')
        self.login(self.tech)
        self.client.post(reverse('repair-part-add', args=[rep.pk]), {'part': self.part.pk, 'quantity': 99})
        self.part.refresh_from_db(); self.assertEqual(self.part.stock, 10)
        self.assertEqual(rep.parts.count(), 0)

    def test_technician_only_own_repairs(self):
        rep = self.new_repair(Repair.ASSIGNED, self.tech, 'x')
        self.login(self.tech2)
        self.assertEqual(self.client.get(reverse('repair-detail', args=[rep.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('repair-start', args=[rep.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse('repair-invoice', args=[rep.pk])).status_code, 403)
        self.assertNotIn(rep, list(self.client.get(reverse('repair-list')).context['objects']))
        self.login(self.tech)
        self.assertEqual(self.client.get(reverse('repair-detail', args=[rep.pk])).status_code, 200)

    def test_equipment_must_belong_to_customer(self):
        other = Customer.objects.create(name='Lain')
        self.login(self.admin)
        r = self.client.post(reverse('repair-add'), {'customer': other.pk, 'equipment': self.equipment.pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Repair.objects.count(), 0)


class AuthAndRoleTests(BaseCase):
    def status(self, user, name, *args):
        self.login(user)
        return self.client.get(reverse(name, args=args)).status_code

    def test_start_is_login_and_validation(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'auth/login.html')
        r = self.client.post(reverse('login'), {'username': 'adm', 'password': 'salah'})
        self.assertEqual(r.status_code, 200)                       # invalid -> fila ba login
        r = self.client.post(reverse('login'), {'username': 'adm', 'password': 'x12345'})
        self.assertRedirects(r, reverse('dashboard'))              # valid -> dashboard
        self.client.get(reverse('logout'))
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)
        self.assertEqual(list(ActivityLog.objects.filter(user=self.admin).values_list('action', flat=True)[:2]),
                         ['Logout', 'Login'])

    def test_inactive_user_cannot_login(self):
        self.tech.is_active = False
        self.tech.save()
        r = self.client.post(reverse('login'), {'username': 'tek', 'password': 'x12345'})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_all_pages_for_admin(self):
        rep = self.new_repair(Repair.DIAGNOSED, None, 'x')
        for name, args in [('dashboard', []), ('part-list', []), ('part-add', []), ('part-detail', [self.part.pk]),
                           ('part-edit', [self.part.pk]), ('category-list', []), ('category-add', []),
                           ('supplier-list', []), ('supplier-add', []), ('movement-list', []), ('movement-add', []),
                           ('customer-list', []), ('customer-add', []), ('equipment-list', []), ('equipment-add', []),
                           ('repair-list', []), ('repair-add', []), ('repair-detail', [rep.pk]),
                           ('repair-edit', [rep.pk]), ('repair-diagnose', [rep.pk]), ('repair-assign', [rep.pk]),
                           ('reports', []), ('u-list', []), ('user-add', []), ('user-edit', [self.tech.pk]),
                           ('activity-log', []), ('UserProfile', []), ('change-password', []),
                           ('repair-invoice', [rep.pk]), ('about', [])]:
            self.assertEqual(self.status(self.admin, name, *args), 200, name)

    def test_technician_restrictions(self):
        for name in ['category-list', 'supplier-list', 'movement-list', 'reports', 'u-list', 'part-add',
                     'repair-add', 'activity-log']:
            self.assertEqual(self.status(self.tech, name), 403, name)
        for name in ['dashboard', 'part-list', 'repair-list', 'customer-list', 'equipment-list', 'customer-add']:
            self.assertEqual(self.status(self.tech, name), 200, name)

    def test_owner_is_read_only(self):
        for name in ['dashboard', 'part-list', 'movement-list', 'repair-list', 'reports', 'customer-list']:
            self.assertEqual(self.status(self.owner, name), 200, name)
        for name in ['part-add', 'repair-add', 'u-list', 'movement-add', 'customer-add', 'activity-log']:
            self.assertEqual(self.status(self.owner, name), 403, name)
        rep = self.new_repair(Repair.ASSIGNED, self.tech, 'x')
        self.login(self.owner)
        self.assertEqual(self.client.post(reverse('repair-part-add', args=[rep.pk]),
                                          {'part': self.part.pk, 'quantity': 1}).status_code, 403)

    def test_user_management_and_password(self):
        self.login(self.admin)
        r = self.client.post(reverse('user-add'), {'username': 'dora', 'full_name': 'Dora', 'role': 'technician',
                                                   'password': 'abc12345', 'is_active': 'on'})
        self.assertEqual(r.status_code, 302)
        u = User.objects.get(username='dora')
        self.assertTrue(u.check_password('abc12345'))
        self.assertEqual(u.role, 'technician')
        self.client.post(reverse('reset-password', args=[u.pk]))
        u.refresh_from_db(); self.assertTrue(u.check_password('nerafil123'))
        r = self.client.post(reverse('user-edit', args=[self.admin.pk]),
                             {'username': 'adm', 'full_name': 'Admin', 'role': 'owner', 'is_active': 'on'})
        self.assertEqual(r.status_code, 200)       # tidak boleh menurunkan role sendiri
        self.admin.refresh_from_db(); self.assertEqual(self.admin.role, 'admin')


class InventoryTests(BaseCase):
    def test_stock_in_out(self):
        register_movement(self.part, StockMovement.OUT, 4)
        self.part.refresh_from_db(); self.assertEqual(self.part.stock, 6)
        with self.assertRaises(StockError):
            register_movement(self.part, StockMovement.OUT, 7)

    def test_movement_form_and_low_stock(self):
        self.login(self.admin)
        r = self.client.post(reverse('movement-add'), {'part': self.part.pk, 'movement_type': 'out', 'quantity': 8, 'note': 'tes'})
        self.assertEqual(r.status_code, 302)
        self.part.refresh_from_db()
        self.assertEqual(self.part.stock, 2)
        self.assertTrue(self.part.is_low)
        r = self.client.get(reverse('part-list') + '?low=1')
        self.assertIn(self.part, list(r.context['objects']))
        self.assertEqual(self.client.get(reverse('dashboard')).context['n_stock_low'], 1)


class ReportTests(BaseCase):
    def test_pdfs(self):
        rep = self.new_repair(Repair.COMPLETED, self.tech, 'x')
        self.login(self.admin)
        for params in ['type=stock', 'type=movement&date_from=2020-01-01&date_to=2100-01-01',
                       'type=repair&date_from=2020-01-01&date_to=2100-01-01']:
            r = self.client.get(reverse('reports') + '?' + params)
            self.assertEqual(r['Content-Type'], 'application/pdf', params)
            self.assertTrue(r.content.startswith(b'%PDF'))
        r = self.client.get(reverse('repair-invoice', args=[rep.pk]))
        self.assertTrue(r.content.startswith(b'%PDF'))
