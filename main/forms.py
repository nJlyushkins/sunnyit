from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Messages
import re


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Имя пользователя"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}),
        error_messages={
            'required': _("Пожалуйста, введите имя пользователя.")
        }
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
        error_messages={
            'required': _("Пожалуйста, введите пароль.")
        }
    )

    error_messages = {
        'invalid_login': _(
            "Пожалуйста, введите правильное имя пользователя и пароль. "
            "Обратите внимание, что оба поля чувствительны к регистру."
        ),
        'inactive': _("Эта учетная запись неактивна."),
    }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Электронная почта"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
        error_messages={
            'required': _("Пожалуйста, введите email."),
            'invalid': _("Введите корректный email."),
            'unique': _("Пользователь с таким email уже существует.")
        }
    )
    username = forms.CharField(
        label=_("Имя пользователя"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте имя пользователя'}),
        error_messages={
            'required': _("Пожалуйста, введите имя пользователя."),
            'unique': _("Пользователь с таким именем уже существует.")
        }
    )
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
        error_messages={
            'required': _("Пожалуйста, введите пароль.")
        }
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}),
        error_messages={
            'required': _("Пожалуйста, подтвердите пароль.")
        }
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    error_messages = {
        'password_mismatch': _("Пароли не совпадают."),
    }

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # Проверка длины пароля
        if len(password1) < 8:
            raise forms.ValidationError(_("Пароль должен содержать минимум 8 символов."))

        # Проверка на наличие заглавной буквы
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError(_("Пароль должен содержать хотя бы одну заглавную букву."))

        # Проверка на наличие строчной буквы
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError(_("Пароль должен содержать хотя бы одну строчную букву."))

        # Проверка на наличие цифры
        if not re.search(r'\d', password1):
            raise forms.ValidationError(_("Пароль должен содержать хотя бы одну цифру."))

        # Проверка на наличие специального символа
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise forms.ValidationError(_("Пароль должен содержать хотя бы один специальный символ (!@#$%^&*)."))

        return password1

class MessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ['text', 'state']