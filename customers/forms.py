from django import forms
from crispy_forms.layout import Row, Column

from config.forms import bootstrap_widgets, make_helper
from customers.models import Customer, Equipment


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(Row(
            Column('name', css_class='form-group col-md-6 mb-2'),
            Column('phone', css_class='form-group col-md-6 mb-2'),
        ))


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['customer', 'name', 'plate', 'serial_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(
            Row(
                Column('customer', css_class='form-group col-md-6 mb-2'),
                Column('name', css_class='form-group col-md-6 mb-2'),
            ),
            Row(
                Column('plate', css_class='form-group col-md-4 mb-2'),
                Column('serial_number', css_class='form-group col-md-8 mb-2'),
            ),
        )

    def clean_plate(self):
        return self.cleaned_data['plate'].strip().upper()
