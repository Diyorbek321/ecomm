from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']

        # Split full name into first_name and last_name
        full_name = self.cleaned_data['full_name'].strip()
        if ' ' in full_name:
            first_name, last_name = full_name.rsplit(' ', 1)
            user.first_name = first_name
            user.last_name = last_name
        else:
            user.first_name = full_name
            user.last_name = ''

        if commit:
            user.save()
        return user