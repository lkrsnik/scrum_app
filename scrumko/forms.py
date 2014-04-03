# -*- coding: utf-8 -*-

from django import forms

from scrumko.models import UserProfile, Sprint, Project
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.defaultfilters import mark_safe

my_default_errors = {
    'required': 'This field is required',
    'invalid': 'Enter a valid value'
}

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
	
	project_name = forms.ModelChoiceField(queryset=Project.objects.all(), required=True, label = mark_safe('Ime projekta'), error_messages=my_default_errors)
	start_date = forms.DateField(label = mark_safe(u'Datum začetka'), required=True, error_messages=my_default_errors)
	finish_date = forms.DateField(label = mark_safe(u'Datum zaključka'))
	velocity = forms.IntegerField(label = mark_safe(u'Predvidena hitrost'))
	
	class Meta:
		model = Sprint
		
class ProjectCreateForm(forms.ModelForm):

    project_name =  forms.CharField(max_length=50, help_text="Ime projekta")
    #project_owner =  models.ForeignKey(widget=forms.HiddenInput())
    #scrum_master = models.ForeignKey(widget=forms.HiddenInput())
    #team = models.ManyToManyField(widget=forms.HiddenInput())

    class Meta:
        model = Project
        






