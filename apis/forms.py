from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'email', 'password1', 'password2', 'user_type']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")