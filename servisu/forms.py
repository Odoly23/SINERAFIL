from django import forms
from crispy_forms.layout import Row, Column

from cliente.models import Motor
from config.forms import bootstrap_widgets, make_helper
from pesa.forms import DateInput
from pesa.models import Pesa
from servisu.models import Despeza, Servisu
from users.models import Emp


class MotorSelect(forms.Select):
    """Select motór ho atributu data-kliente atu bele filtra ho JS."""

    def __init__(self, *args, motor_kliente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.motor_kliente = motor_kliente or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opt = super().create_option(name, value, label, selected, index, subindex, attrs)
        key = getattr(value, 'value', value)
        if key in self.motor_kliente:
            opt['attrs']['data-kliente'] = self.motor_kliente[key]
        return opt


class ServisuForm(forms.ModelForm):
    class Meta:
        model = Servisu
        fields = ['date', 'kliente', 'motor', 'mekanik', 'complaint', 'labor_cost', 'discount',
                  'mech_percent', 'status', 'note']
        widgets = {
            'date': DateInput(),
            'complaint': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {'mech_percent': 'Husik mamuk atu uza persentajen mekániku nian.'}

    def __init__(self, *args, emp=None, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['mech_percent'].required = False
        if not self.instance.pk:
            self.initial['mech_percent'] = None
        self.fields['mekanik'].queryset = Emp.objects.filter(
            account__user__groups__name='mekaniku', account__user__is_active=True)
        mapping = {m.pk: m.kliente_id for m in Motor.objects.all()}
        self.fields['motor'].widget = MotorSelect(attrs={'class': 'form-control'}, motor_kliente=mapping)
        self.fields['motor'].queryset = Motor.objects.select_related('kliente')
        self._own_only = group == 'mekaniku'
        self._emp = emp
        if self._own_only:
            # mekániku rasik: mekániku no persentajen otomátiku (la hatudu iha form)
            self.fields['mekanik'].required = False
        mech_row = [] if self._own_only else [
            Row(
                Column('mekanik', css_class='form-group col-md-4 mb-2'),
                Column('mech_percent', css_class='form-group col-md-2 mb-2'),
            )]
        self.helper = make_helper(
            Row(
                Column('date', css_class='form-group col-md-2 mb-2'),
                Column('kliente', css_class='form-group col-md-5 mb-2'),
                Column('motor', css_class='form-group col-md-5 mb-2'),
            ),
            Row(Column('complaint', css_class='form-group col-md-12 mb-2')),
            Row(
                Column('labor_cost', css_class='form-group col-md-3 mb-2'),
                Column('discount', css_class='form-group col-md-3 mb-2'),
                Column('status', css_class='form-group col-md-3 mb-2'),
            ),
            *mech_row,
            Row(Column('note', css_class='form-group col-md-12 mb-2')),
        )

    def clean(self):
        data = super().clean()
        if self._own_only:
            data['mekanik'] = self.instance.mekanik if self.instance.pk else self._emp
            data['mech_percent'] = self.instance.mech_percent if self.instance.pk else None
            self.errors.pop('mekanik', None)
            if data['mekanik'] is None:
                raise forms.ValidationError('Konta ne\'e la liga ho funcionariu mekániku.')
        kliente, motor = data.get('kliente'), data.get('motor')
        if kliente and motor and motor.kliente_id != kliente.pk:
            self.add_error('motor', "Motór ne'e la pertense ba kliente ne'ebé hili.")
        if (data.get('discount') or 0) < 0:
            self.add_error('discount', 'Diskaun la bele negativu.')
        return data

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.mekanik = self.cleaned_data['mekanik']
        if self.cleaned_data.get('mech_percent') in (None, ''):
            obj.mech_percent = obj.mekanik.persen_ongkos
        if commit:
            obj.save()
        return obj


class AddPesaForm(forms.Form):
    pesa = forms.ModelChoiceField(label='Pesa', queryset=Pesa.objects.none())
    quantity = forms.IntegerField(label='Kuantidade', min_value=1, initial=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['pesa'].queryset = Pesa.objects.filter(is_active=True, stock__gt=0)
        self.fields['pesa'].label_from_instance = (
            lambda p: '%s — %s  (stock: %s, $ %s)' % (p.code, p.name, p.stock, p.price_sell))


class DespezaForm(forms.ModelForm):
    class Meta:
        model = Despeza
        fields = ['date', 'description', 'amount']
        widgets = {'date': DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.helper = make_helper(
            Row(
                Column('date', css_class='form-group col-md-3 mb-2'),
                Column('description', css_class='form-group col-md-6 mb-2'),
                Column('amount', css_class='form-group col-md-3 mb-2'),
            ),
        )
