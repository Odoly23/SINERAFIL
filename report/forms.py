from django import forms
from django.utils import timezone

from config.forms import bootstrap_widgets


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(**kwargs)


class ReportForm(forms.Form):
    TIPU = [
        ('stock', 'Stock pesa-rezerva (atuál)'),
        ('movement', 'Stock tama no sai (movimentu)'),
        ('repair', 'Reparasaun / finanseiru'),
    ]
    type = forms.ChoiceField(label='Tipu relatóriu', choices=TIPU)
    date_from = forms.DateField(label='Husi data', widget=DateInput(), required=False)
    date_to = forms.DateField(label="To'o data", widget=DateInput(), required=False)
    movement = forms.ChoiceField(
        label='Tipu movimentu', required=False,
        choices=[('', 'Tama no Sai'), ('in', "Tama de'it"), ('out', "Sai de'it")])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        today = timezone.localdate()
        self.fields['date_from'].initial = today.replace(day=1)
        self.fields['date_to'].initial = today

    def clean(self):
        d = super().clean()
        today = timezone.localdate()
        d['date_from'] = d.get('date_from') or today.replace(day=1)
        d['date_to'] = d.get('date_to') or today
        if d['date_from'] > d['date_to']:
            raise forms.ValidationError('Data hahu tenke sei molok data remata.')
        return d
