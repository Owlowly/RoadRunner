from django import forms
from localflavor.us.forms import USZipCodeField
from django.contrib.auth.models import User
from .models import Profile
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput, label=_('Email'))
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Repeat password'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']


    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(_("Passwords don't match"))
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(_('Email already in use.'))
        return data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    postal_code = USZipCodeField()
    class Meta:
        model = Profile
        fields = ['address', 'city', 'postal_code']

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id).filter(email=data)
        if qs.exists():
            raise forms.ValidationError(_('Email already in use.'))
        return data

