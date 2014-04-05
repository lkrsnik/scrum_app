# -*- coding: utf-8 -*-

from django import forms
from django.core.validators import RegexValidator
from scrumko.models import UserProfile, Sprint, Project, Story
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.defaultfilters import mark_safe
from django.core.exceptions import ValidationError
from datetime import date, datetime

sprint_error = {
    'required': 'To polje je obvezno.',    
}
required_error = {
	'required': 'To polje je obvezno.',
}
velocity_error = {
	'required': 'To polje je obvezno.',    
	'invalid': 'Prosim vpišite celo število',
}



class UserForm(forms.ModelForm):
    password = forms.CharField(label = mark_safe(u'Geslo'), widget=forms.PasswordInput(), error_messages=required_error)
    email = forms.EmailField(label = mark_safe(u'Email'), error_messages=required_error)
    is_superuser = forms.BooleanField(label = mark_safe(u'Administrator'), required=False)

    username = 	forms.CharField(label = mark_safe(u'Uporabniško ime'), error_messages=required_error)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_superuser')

class UserProfileForm(forms.ModelForm):
    picture = forms.ImageField(label = mark_safe(u'Prikazna slika'), required=False)
    class Meta:
        model = UserProfile
        fields = ('picture',)

		
class ProjectCreateForm(forms.ModelForm):

    project_name =  forms.CharField(max_length=50, help_text="Ime projekta")
    #project_owner =  models.ForeignKey(widget=forms.HiddenInput())
    #scrum_master = models.ForeignKey(widget=forms.HiddenInput())
    #team = models.ManyToManyField(widget=forms.HiddenInput())

    class Meta:
        model = Project
        
class SprintCreateForm(forms.ModelForm):
	
	
	project_name = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())
	start_date = forms.DateField(label = mark_safe(u'Datum začetka'), error_messages=sprint_error)	
	finish_date = forms.DateField(label = mark_safe(u'Datum zaključka'), error_messages=sprint_error)	
	velocity = forms.IntegerField(label = mark_safe(u'Predvidena hitrost'), error_messages=velocity_error, validators=[
		RegexValidator(
			regex='^[0-9]*$',
			message='Hitrost mora biti pozitivno celo število',
			code='invalid_value'
		),
	])   
    		
    
    # for validating date
	def clean_start_date(self):
		start_date = self.cleaned_data['start_date']
		project_name_id = self.cleaned_data['project_name']
		
		#covering with the other sprint
		covering = Sprint.objects.filter(start_date__gte=start_date, finish_date__lte=start_date, project_name = project_name_id)
		
		print len(covering)
		
		if len(covering) > 0:
			raise ValidationError("Datum se prekriva z drugo iteracijo.")
			return
		
		# check if not in past
		if start_date < date.today():
			raise ValidationError("Ne smete vnašati preteklih datumov.")
			return
		
		
		
								
		return start_date
		
	def clean_finish_date(self):
		end_date = self.cleaned_data['finish_date']
		project_name_id = self.cleaned_data['project_name']
		
		#covering with the other sprint
		covering = Sprint.objects.filter(start_date__gte=end_date, finish_date__lte=end_date, project_name = project_name_id)
					
		if len(covering) > 0:
			raise ValidationError("Datum se prekriva z drugo iteracijo.")
			return
		
		# check if not in past
		if end_date < date.today():
			raise ValidationError("Ne smete vnašati preteklih datumov.")
			return
			
		# check if start berfore end
		start_date = self.data.get('start_date')
		
		start_date = datetime.strptime(start_date, "%m/%d/%Y").date()
		
		if end_date < start_date:
			raise ValidationError("Začetek iteracije mora biti pred koncem.")
			return
								
		return end_date
		
	
	class Meta:
		model = Sprint

class StoryForm (forms.ModelForm):
	
	project_name = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())
	story_name = forms.CharField(label = mark_safe('Ime uporabniške zgodbe'), error_messages=required_error)
	text = forms.CharField(label = mark_safe('Opis uporabniške zgodbe'), widget=forms.Textarea, error_messages=required_error)
	bussines_value = forms.IntegerField(label = mark_safe('Poslovna vrednost'), error_messages=velocity_error, validators=[
		RegexValidator(
			regex='^[0-9]*$',
			message='Vpišite pozitivno celo število',
			code='invalid'
		),
	])
	
		
	priority = forms.TypedChoiceField(label = mark_safe('Prioriteta'), choices=Story.PRIORITY_CHOICES)
	test_text = forms.CharField(label = mark_safe('Sprejemni testi'), widget=forms.Textarea, error_messages=required_error)
	
	class Meta:
		model = Story
		
	def clean_story_name(self):
		story_name_new = self.cleaned_data['story_name']
		project_name_id = self.cleaned_data['project_name']
		
		#covering with the other story name
		covering = Story.objects.filter(story_name = story_name_new, project_name = project_name_id)
					
		if len(covering) > 0:
			raise ValidationError("Zgodba z enakim imenom že obstaja.")
			return
		
		return story_name_new
	
	






