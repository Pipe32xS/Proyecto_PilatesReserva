# login/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Correo o usuario"
        self.fields['username'].widget.attrs.update({
            "class": "form-control form-control-sm",
            "placeholder": "Correo o usuario",
            "autocomplete": "username",
            "required": True,
        })
        self.fields['password'].label = "Contraseña"
        self.fields['password'].widget.attrs.update({
            "class": "form-control form-control-sm",
            "placeholder": "Contraseña",
            "autocomplete": "current-password",
            "required": True,
        })


class RegistroClienteForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Correo electrónico',
            'required': True,
        })
    )
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Nombre de usuario',
            'required': True,
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Contraseña',
            'required': True,
        })
    )
    password2 = forms.CharField(
        label="Repite la contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Repite la contraseña',
            'required': True,
        })
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('El correo ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                'El nombre de usuario ya está registrado.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if hasattr(user, "rol") and not user.rol:
            user.rol = "cliente"
        if commit:
            user.save()
        return user
