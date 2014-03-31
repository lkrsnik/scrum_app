from django import forms

from scrumko.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)



class StatusForm(forms.Form):
    administrator = forms.BooleanField(required=False)



