from django import forms
from crispy_forms.layout import Row, Column

from config.forms import bootstrap_widgets, make_helper
from inventory.models import Part, StockMovement


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['sku', 'name', 'category', 'supplier', 'minimum_stock', 'purchase_price', 'selling_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(
            Row(
                Column('sku', css_class='form-group col-md-3 mb-2'),
                Column('name', css_class='form-group col-md-9 mb-2'),
            ),
            Row(
                Column('category', css_class='form-group col-md-6 mb-2'),
                Column('supplier', css_class='form-group col-md-6 mb-2'),
            ),
            Row(
                Column('purchase_price', css_class='form-group col-md-4 mb-2'),
                Column('selling_price', css_class='form-group col-md-4 mb-2'),
                Column('minimum_stock', css_class='form-group col-md-4 mb-2'),
            ),
        )


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['part', 'movement_type', 'quantity', 'note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(
            Row(
                Column('part', css_class='form-group col-md-6 mb-2'),
                Column('movement_type', css_class='form-group col-md-3 mb-2'),
                Column('quantity', css_class='form-group col-md-3 mb-2'),
            ),
            Row(Column('note', css_class='form-group col-md-12 mb-2')),
        )

    def clean_quantity(self):
        q = self.cleaned_data['quantity']
        if q <= 0:
            raise forms.ValidationError('Kuantidade tenke boot liu 0.')
        return q
