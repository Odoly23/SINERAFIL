from django import forms
from crispy_forms.layout import Row, Column

from cliente.models import Kliente, Motor
from config.forms import bootstrap_widgets, make_helper


class KlienteForm(forms.ModelForm):
    class Meta:
        model = Kliente
        fields = ['name', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(
            Row(
                Column('name', css_class='form-group col-md-4 mb-2'),
                Column('phone', css_class='form-group col-md-3 mb-2'),
                Column('address', css_class='form-group col-md-5 mb-2'),
            ),
        )


class MotorForm(forms.ModelForm):
    class Meta:
        model = Motor
        fields = ['kliente', 'plate', 'brand', 'model_name', 'year', 'color']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(
            Row(
                Column('kliente', css_class='form-group col-md-4 mb-2'),
                Column('plate', css_class='form-group col-md-2 mb-2'),
                Column('brand', css_class='form-group col-md-2 mb-2'),
                Column('model_name', css_class='form-group col-md-2 mb-2'),
                Column('year', css_class='form-group col-md-1 mb-2'),
                Column('color', css_class='form-group col-md-1 mb-2'),
            ),
        )

    def clean_plate(self):
        return self.cleaned_data['plate'].strip().upper()
