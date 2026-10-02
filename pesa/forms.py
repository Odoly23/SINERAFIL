from django import forms
from crispy_forms.layout import Row, Column

from config.forms import bootstrap_widgets, make_helper
from pesa.models import MovimentuStock, Pesa


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(**kwargs)


class PesaForm(forms.ModelForm):
    class Meta:
        model = Pesa
        fields = ['code', 'name', 'kategoria', 'unit', 'price_buy', 'price_sell', 'stock_min',
                  'description', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(
            Row(
                Column('code', css_class='form-group col-md-3 mb-2'),
                Column('name', css_class='form-group col-md-6 mb-2'),
                Column('kategoria', css_class='form-group col-md-3 mb-2'),
            ),
            Row(
                Column('unit', css_class='form-group col-md-2 mb-2'),
                Column('price_buy', css_class='form-group col-md-3 mb-2'),
                Column('price_sell', css_class='form-group col-md-3 mb-2'),
                Column('stock_min', css_class='form-group col-md-2 mb-2'),
                Column('is_active', css_class='form-group col-md-2 mb-2 pt-4'),
            ),
            Row(Column('description', css_class='form-group col-md-12 mb-2')),
        )


class MovimentuForm(forms.ModelForm):
    class Meta:
        model = MovimentuStock
        fields = ['pesa', 'tipu', 'quantity', 'price', 'date', 'reference', 'note']
        widgets = {'date': DateInput(), 'note': forms.Textarea(attrs={'rows': 2})}
        help_texts = {'price': 'Husik 0 atu uza folin pesa nian.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['pesa'].queryset = Pesa.objects.filter(is_active=True)
        self.fields['price'].required = False
        self.helper = make_helper(
            Row(
                Column('pesa', css_class='form-group col-md-6 mb-2'),
                Column('tipu', css_class='form-group col-md-2 mb-2'),
                Column('quantity', css_class='form-group col-md-2 mb-2'),
                Column('date', css_class='form-group col-md-2 mb-2'),
            ),
            Row(
                Column('price', css_class='form-group col-md-3 mb-2'),
                Column('reference', css_class='form-group col-md-9 mb-2'),
            ),
            Row(Column('note', css_class='form-group col-md-12 mb-2')),
        )

    def clean_quantity(self):
        q = self.cleaned_data['quantity']
        if q <= 0:
            raise forms.ValidationError('Kuantidade tenke boot liu 0.')
        return q
