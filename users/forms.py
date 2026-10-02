from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML

from config.forms import bootstrap_widgets, make_helper
from users.models import Emp, EmpUser

GROUP_CHOICES = [('admin', 'Admin'), ('mekaniku', 'Mekániku'), ('nain', "Na'in ba Ofisina")]


class EmpForm(forms.ModelForm):
    """Dadus funcionariu + konta (username, papél, password) iha form ida de'it."""
    username = forms.CharField(label='Naran utilizadór', max_length=150)
    group = forms.ChoiceField(label='Papél', choices=GROUP_CHOICES)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(render_value=False), required=False,
                               help_text='Husik mamuk atu la troka password (bainhira edita).')
    is_active = forms.BooleanField(label='Konta ativu', required=False, initial=True)

    class Meta:
        model = Emp
        fields = ['name', 'sexo', 'phone', 'email', 'persen_ongkos']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['name'].required = True
        self.fields['sexo'].required = True
        empuser = EmpUser.objects.filter(emp=self.instance).select_related('user').first() if self.instance.pk else None
        self._user = empuser.user if empuser else None
        if self._user:
            self.fields['username'].initial = self._user.username
            self.fields['group'].initial = self._user.groups.first().name if self._user.groups.exists() else 'mekaniku'
            self.fields['is_active'].initial = self._user.is_active
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = ''
        self.helper = make_helper(
            Row(
                Column('name', css_class='form-group col-md-4 mb-2'),
                Column('sexo', css_class='form-group col-md-2 mb-2'),
                Column('phone', css_class='form-group col-md-3 mb-2'),
                Column('email', css_class='form-group col-md-3 mb-2'),
            ),
            HTML('<hr><h6 class="text-muted">Konta utilizadór</h6>'),
            Row(
                Column('username', css_class='form-group col-md-4 mb-2'),
                Column('group', css_class='form-group col-md-3 mb-2'),
                Column('password', css_class='form-group col-md-3 mb-2'),
                Column('persen_ongkos', css_class='form-group col-md-2 mb-2'),
            ),
            Row(Column('is_active', css_class='form-group col-md-4 mb-2')),
        )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username__iexact=username)
        if self._user:
            qs = qs.exclude(pk=self._user.pk)
        if qs.exists():
            raise forms.ValidationError('Naran utilizadór ne\'e uza ona.')
        return username


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label='Password atual', widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}))
    new_password1 = forms.CharField(label='Password foun', max_length=100, widget=forms.PasswordInput())
    new_password2 = forms.CharField(label='Konfirma password foun', max_length=100, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        self.fields['new_password1'].help_text = ''
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('old_password', css_class='form-group col-md-12 mb-0'), css_class='form-row'),
            Row(Column('new_password1', css_class='form-group col-md-12 mb-0'), css_class='form-row'),
            Row(Column('new_password2', css_class='form-group col-md-12 mb-0'), css_class='form-row'),
            HTML(""" <button class="btn btn-sm btn-primary" type="submit">Alterar <i class="fa fa-save"></i></button> """)
        )
