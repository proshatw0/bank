from django import forms


class LoginForm(forms.Form):
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'phone', 'id': 'phone-in', 'placeholder': 'Телефон'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'password', 'id': 'password-in', 'placeholder': 'Пароль'}))

class RegistrationForm(forms.Form):
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'phone', 'id': 'phone', 'placeholder': 'Телефон'}))
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'class': 'email', 'id': 'email', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'password', 'id': 'password', 'placeholder': 'Пароль'}))
    retry_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'retry-password', 'id': 'retry-password', 'placeholder': 'Повторите пароль'}))
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'name', 'id': 'name', 'placeholder': 'Имя'}))
    surname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'surname', 'id': 'surname', 'placeholder': 'Фамилия'}))
    middle_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'middle_name', 'id': 'middle_name', 'placeholder': 'Отчество (при наличии)'}))
    passport_serial = forms.CharField(max_length=4, widget=forms.TextInput(attrs={'id': 'passport-serial', 'placeholder': 'Серия'}))
    passport_number = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'id': 'passport-number', 'placeholder': 'Номер'}))
    passport_issue_date = forms.DateField(widget=forms.DateInput(attrs={'id': 'passport-issue-date', 'type': 'date'}))
    passport_issuer = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'passport-issuer', 'id': 'passport-issuer', 'placeholder': 'Кем выдан'}))
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'id': 'birth-date', 'type': 'date'}))

class PinCode(forms.Form):
    text = ""
    one = forms.CharField(max_length=1, widget=forms.TextInput(attrs={'class': 'input-pin', 'id': 'one'}))
    two = forms.CharField(max_length=1, widget=forms.TextInput(attrs={'class': 'input-pin', 'id': 'two'}))
    three = forms.CharField(max_length=1, widget=forms.TextInput(attrs={'class': 'input-pin', 'id': 'three'}))
    four = forms.CharField(max_length=1, widget=forms.TextInput(attrs={'class': 'input-pin input-pin-last', 'id': 'four'}))