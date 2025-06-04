from django import forms
from django.contrib.auth.forms import UsernameField, AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class AuthForm(AuthenticationForm):
    username = UsernameField(label='Логин',widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SignUpForm(UserCreationForm):
    username = UsernameField(label='Логин',widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Электронная почта',widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    usable_password = None

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class GroupAdd(forms.Form):
    group_id = forms.CharField(label='ID группы',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

class CodeAdd(forms.Form):
    group_id = forms.CharField(label='ID группы',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    code = forms.CharField(label='Код подтверждения',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    token = forms.CharField(label='Токен',
                            widget=forms.TextInput(attrs={'class': 'form-control'}))