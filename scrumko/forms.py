from django import forms

from scrumko.models import UserProfile, Sprint
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_superuser', 'is_staff')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)

class SprintCreateForm(forms.ModelForm):
    class Meta:
        model = Sprint
        





