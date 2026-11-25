from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML

from config.forms import bootstrap_widgets, make_helper
from users.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(render_value=False), required=False,
                               help_text='Husik mamuk atu la troka password (bainhira edita).')

    class Meta:
        model = User
        fields = ['username', 'full_name', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_widgets(self)
        if not self.instance.pk:
            self.fields['password'].required = True
            self.fields['password'].help_text = ''
        self.helper = make_helper(
            Row(
                Column('username', css_class='form-group col-md-4 mb-2'),
                Column('full_name', css_class='form-group col-md-4 mb-2'),
                Column('role', css_class='form-group col-md-4 mb-2'),
            ),
            Row(
                Column('password', css_class='form-group col-md-6 mb-2'),
                Column('is_active', css_class='form-group col-md-6 mb-2 pt-4'),
            ),
        )

    def clean_password(self):
        pw = self.cleaned_data.get('password')
        if pw:
            password_validation.validate_password(pw, self.instance)
        return pw

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        elif not user.pk:
            user.set_unusable_password()
        if commit:
            user.save()
        return user


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
