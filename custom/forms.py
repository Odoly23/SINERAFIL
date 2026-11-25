from django import forms
from crispy_forms.layout import Row, Column

from config.forms import bootstrap_widgets, make_helper
from custom.models import Category, Supplier


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(Row(Column('name', css_class='form-group col-md-6 mb-2')))


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(Row(
            Column('name', css_class='form-group col-md-6 mb-2'),
            Column('phone', css_class='form-group col-md-6 mb-2'),
        ))
