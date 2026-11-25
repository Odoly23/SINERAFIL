from django import forms
from crispy_forms.layout import Row, Column

from config.forms import bootstrap_widgets, make_helper
from customers.models import Equipment
from inventory.models import Part
from repairs.models import Repair
from users.models import User


class EquipmentSelect(forms.Select):
    """Select ekipamentu ho atributu data-customer atu bele filtra ho JS."""

    def __init__(self, *args, equipment_customer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipment_customer = equipment_customer or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opt = super().create_option(name, value, label, selected, index, subindex, attrs)
        key = getattr(value, 'value', value)
        if key in self.equipment_customer:
            opt['attrs']['data-customer'] = self.equipment_customer[key]
        return opt


class RepairForm(forms.ModelForm):
    """Etapa 1: Register New Repair (Customer and Equipment Data)."""
    class Meta:
        model = Repair
        fields = ['customer', 'equipment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        mapping = {e.pk: e.customer_id for e in Equipment.objects.all()}
        self.fields['equipment'].widget = EquipmentSelect(attrs={'class': 'form-control'}, equipment_customer=mapping)
        self.fields['equipment'].queryset = Equipment.objects.select_related('customer')
        self.helper = make_helper(Row(
            Column('customer', css_class='form-group col-md-6 mb-2'),
            Column('equipment', css_class='form-group col-md-6 mb-2'),
        ))

    def clean(self):
        data = super().clean()
        customer, equipment = data.get('customer'), data.get('equipment')
        if customer and equipment and equipment.customer_id != customer.pk:
            self.add_error('equipment', "Ekipamentu ne'e la pertense ba kliente ne'ebé hili.")
        return data


class DiagnosisForm(forms.ModelForm):
    """Etapa 2: Damage Diagnosis."""
    class Meta:
        model = Repair
        fields = ['diagnosis']
        widgets = {'diagnosis': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['diagnosis'].required = True
        self.helper = make_helper(Row(Column('diagnosis', css_class='form-group col-md-12 mb-2')))


class AssignForm(forms.ModelForm):
    """Etapa 3: Assign Technician."""
    class Meta:
        model = Repair
        fields = ['technician']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['technician'].required = True
        self.fields['technician'].queryset = User.objects.filter(role=User.TECHNICIAN, is_active=True)
        self.fields['technician'].label_from_instance = lambda u: u.display_name
        self.helper = make_helper(Row(Column('technician', css_class='form-group col-md-6 mb-2')))


class CompleteForm(forms.ModelForm):
    """Etapa 6: Confirm Completion (ongkos servisu)."""
    class Meta:
        model = Repair
        fields = ['service_cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(Row(Column('service_cost', css_class='form-group col-md-4 mb-2')))

    def clean_service_cost(self):
        v = self.cleaned_data['service_cost']
        if v < 0:
            raise forms.ValidationError('Ongkos labele negativu.')
        return v


class AddPartForm(forms.Form):
    """Etapa 4: Spare Parts Usage."""
    part = forms.ModelChoiceField(label='Pesa', queryset=Part.objects.none())
    quantity = forms.IntegerField(label='Kuantidade', min_value=1, initial=1)
    unit_price = forms.DecimalField(label='Folin (USD) — husik mamuk = folin faan', required=False,
                                    min_value=0, max_digits=12, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['part'].queryset = Part.objects.filter(stock__gt=0)
        self.fields['part'].label_from_instance = (
            lambda p: '%s — %s  (stock: %s, $ %s)' % (p.sku, p.name, p.stock, p.selling_price))
