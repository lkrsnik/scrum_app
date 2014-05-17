# -*- coding: utf-8 -*-

from django import forms
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from django.core import validators
from scrumko.models import UserProfile, Sprint, Project, Story, NotificationPermission, Task, Work_Time
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.defaultfilters import mark_safe
from django.core.exceptions import ValidationError
from datetime import date, datetime
from decimal import *

sprint_error = {
    'required': 'Required.',    
}
required_error = {
	'required':  'Required.',  
}
velocity_error = {
	'required':  'Required.',     
	'invalid': 'Please enter a positive integer.',
}



class UserForm(forms.ModelForm):

    email = forms.EmailField(label = mark_safe(u'Email'), error_messages=required_error)
    is_superuser = forms.BooleanField(label = mark_safe(u'Administrator'), required=False)
    username = 	forms.CharField(label = mark_safe(u'Username'), error_messages=required_error)
    first_name = forms.CharField(label = mark_safe(u'Name'), error_messages=required_error)
    last_name = forms.CharField(label = mark_safe(u'Surname'), error_messages=required_error)
    password = forms.CharField(widget=forms.PasswordInput(), label="Password", error_messages=required_error)
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Repeat password", error_messages=required_error)

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return self.data['password']
	
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'is_superuser','password',)
        
class UserEditForm(forms.ModelForm):

	email = forms.EmailField(label = mark_safe(u'Email'), error_messages=required_error)
	is_superuser = forms.BooleanField(label = mark_safe(u'Administrator'), required=False)
	username = 	forms.CharField(label = mark_safe(u'Username'), error_messages=required_error)
	first_name = forms.CharField(label = mark_safe(u'Name'), error_messages=required_error)
	last_name = forms.CharField(label = mark_safe(u'Surname'), error_messages=required_error)
	password = forms.CharField(required=False, widget=forms.PasswordInput(), label="Password", error_messages=required_error)
	password2 = forms.CharField(required=False, widget=forms.PasswordInput(), label="Repeat password", error_messages=required_error)

	def clean_password(self):
		if self.data['password'] != self.data['password2']:
			raise forms.ValidationError('Passwords do not match.')
		return self.data['password']

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'is_superuser','password',)
        
	#def validate_unique(self, *args, **kwargs):
	#	return self
	
class UserOrientedEditForm(forms.ModelForm):
	email = forms.EmailField(label = mark_safe(u'Email'), error_messages=required_error)
	is_superuser = forms.BooleanField(widget=forms.HiddenInput(), required=False)
	username = 	forms.CharField(label = mark_safe(u'Username'), error_messages=required_error)
	first_name = forms.CharField(label = mark_safe(u'Name'), error_messages=required_error)
	last_name = forms.CharField(label = mark_safe(u'Surname'), error_messages=required_error)
	password = forms.CharField(required=False, widget=forms.PasswordInput(), label="Password", error_messages=required_error)
	password2 = forms.CharField(required=False, widget=forms.PasswordInput(), label="Repeat password", error_messages=required_error)

	def clean_password(self):
		if self.data['password'] != self.data['password2']:
			raise forms.ValidationError('Passwords do not match.')
		return self.data['password']

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'is_superuser','password',)

    
class UserProfileForm(forms.ModelForm):
    picture = forms.ImageField(label = mark_safe(u'Prikazna slika'), required=False)
    class Meta:
        model = UserProfile
        fields = ('picture',)

class NotificationPermissionForm(forms.ModelForm):
	permission = forms.BooleanField(label = mark_safe(u'Allow story notifications'), required=False)
	class Meta:
		model= NotificationPermission
		fields = ('permission',)
		
class ProjectCreateForm(forms.ModelForm):

	project_name =  forms.CharField(label = mark_safe(u'Project name'),max_length=50, error_messages=required_error)
	project_owner =  forms.ModelChoiceField(label = mark_safe(u'Product owner'),queryset=User.objects.all().order_by('username'),error_messages=required_error)
	scrum_master = forms.ModelChoiceField(label = mark_safe(u'Scrum master'),queryset=User.objects.all().order_by('username'),error_messages=required_error)
	team = forms.ModelMultipleChoiceField(widget=forms.HiddenInput(),queryset=User.objects.none(), required=False)
	
	
	#already exist validation
	def clean_project_name(self):
		project_name = self.cleaned_data['project_name']
		
		covering = Project.objects.filter(project_name=project_name)
		if len(covering) > 0:
			raise ValidationError("This project name already exists.")
			return
		return project_name
	
	#validate if name already taken under other roles
	def clean_scrum_master(self):
		scrum_master = self.cleaned_data['scrum_master']
		try:
			project_owner = self.cleaned_data['project_owner']
		except KeyError:
			return scrum_master
		
		if scrum_master==project_owner:
			raise ValidationError("Role "+str(scrum_master)+" is already taken.")
			return
		return scrum_master
	
		
	class Meta:
		model = Project
        
class SprintCreateForm(forms.ModelForm):	
	project_name = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())
	start_date = forms.DateField(label = mark_safe(u'Begining'), error_messages=sprint_error)	
	finish_date = forms.DateField(label = mark_safe(u'End'), error_messages=sprint_error)	
	velocity = forms.IntegerField(label = mark_safe(u'Planned velocity'), error_messages=velocity_error, validators=[
		RegexValidator(
			regex='^[1-9][0-9]*$',
			message='Please enter a positive integer.',
			code='invalid_value'
		),
	])   
    		
    
    # for validating date
	def clean_start_date(self):
		start_date = self.cleaned_data['start_date']
		project_name_id = self.cleaned_data['project_name']
		
		print project_name_id
	
		#covering with the other sprint
		covering = Sprint.objects.filter(start_date__lte=start_date, finish_date__gte=start_date, project_name=project_name_id)
		
		
		print len(covering)
		
		if len(covering) > 0:
			raise ValidationError("Date overlaps with another sprint.")
			return
		
		# check if not in past
		if start_date < date.today():
			raise ValidationError("Do not enter past dates.")
			return					
		return start_date
		
	def clean_finish_date(self):
		end_date = self.cleaned_data['finish_date']
		project_name_id = self.cleaned_data['project_name']
		
		#covering with the other sprint
		covering = Sprint.objects.filter(start_date__lte=end_date, finish_date__gte=end_date, project_name=project_name_id)
					
		if len(covering) > 0:
			raise ValidationError("Date overlaps with another sprint.")
			return
		
		# check if not in past
		if end_date < date.today():
			raise ValidationError("Do not enter past dates.")
			return
			
		# check if start berfore end
		start_date = self.data.get('start_date')
		
		try:
			start_date = datetime.strptime(start_date, "%m/%d/%Y").date()
		except:
			return end_date
						
		if end_date < start_date:
			raise ValidationError("Begining date must be before end date.")
			return 
		
								
		return end_date
		
	
	class Meta:
		model = Sprint

class SprintEditForm(forms.ModelForm):	
	project_name = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())
	start_date = forms.DateField(label = mark_safe(u'Begining'), error_messages=sprint_error)	
	finish_date = forms.DateField(label = mark_safe(u'End'), error_messages=sprint_error)	
	velocity = forms.IntegerField(label = mark_safe(u'Planned velocity'), error_messages=velocity_error, validators=[
		RegexValidator(
			regex='^[1-9][0-9]*$',
			message='Please enter a positive integer.',
			code='invalid_value'
		),
	])   
    		
    
    # for validating date
	def clean_start_date(self):
		start_date = self.cleaned_data['start_date']
		project_name_id = self.cleaned_data['project_name']
		
		print project_name_id
	
		#covering with the other sprint
		covering = Sprint.objects.filter(start_date__lte=start_date, finish_date__gte=start_date, project_name=project_name_id)
		
		
		print len(covering)
		
		if len(covering) > 0:
			raise ValidationError("Date overlaps with another sprint.")
			return
		
		# check if not in past
		if start_date < date.today():
			raise ValidationError("Do not enter past dates.")
			return
		
		
		
								
		return start_date
		
	def clean_finish_date(self):
		end_date = self.cleaned_data['finish_date']
		project_name_id = self.cleaned_data['project_name']
		
		#covering with the other sprint
		covering = Sprint.objects.filter(start_date__lte=end_date, finish_date__gte=end_date, project_name=project_name_id)
					
		if len(covering) > 0:
			raise ValidationError("Date overlaps with another sprint.")
			return
		
		# check if not in past
		if end_date < date.today():
			raise ValidationError("Do not enter past dates.")
			return
			
		# check if start berfore end
		start_date = self.data.get('start_date')
		
		try:
			start_date = datetime.strptime(start_date, "%m/%d/%Y").date()
		except:
			return end_date
						
		if end_date < start_date:
			raise ValidationError("Begining date must be before end date.")
			return 
		
								
		return end_date
		
	
	class Meta:
		model = Sprint

		
class StoryForm (forms.ModelForm):
	
	project_name = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())
	story_name = forms.CharField(label = mark_safe('Name'), error_messages=required_error)
	text = forms.CharField(label = mark_safe('Content'), widget=forms.Textarea, error_messages=required_error)
	bussines_value = forms.IntegerField(label = mark_safe('Bussines value'), error_messages=velocity_error, validators=[
		RegexValidator(
			regex='^[0-9]*$',
			message='Please enter a positive integer.',
			code='invalid'
		),
	])
	
		
	priority = forms.TypedChoiceField(label = mark_safe('Priority'), choices=Story.PRIORITY_CHOICES)
	test_text = forms.CharField(label = mark_safe('Acceptance tests'), widget=forms.Textarea, error_messages=required_error)
	
	class Meta:
		model = Story
		fields = ('project_name', 'story_name', 'text', 'bussines_value', 'priority', 'test_text', )
		
	def clean_story_name(self):
		story_name_new = self.cleaned_data['story_name']
		project_name_id = self.cleaned_data['project_name']
		
		#covering with the other story name
		covering = Story.objects.filter(story_name = story_name_new, project_name = project_name_id)
					
		if len(covering) > 0:
			raise ValidationError("Story with same name already exist.")
			return
		
		return story_name_new
		
class StoryEditForm (forms.ModelForm):
	
	project_name = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())
	story_name = forms.CharField(label = mark_safe('Name'), error_messages=required_error)
	text = forms.CharField(label = mark_safe('Content'), widget=forms.Textarea, error_messages=required_error)
	bussines_value = forms.IntegerField(label = mark_safe('Bussines value'), error_messages=velocity_error, validators=[
		RegexValidator(
			regex='^[0-9]*$',
			message='Please enter a positive integer.',
			code='invalid'
		),
	])
	
		
	priority = forms.TypedChoiceField(label = mark_safe('Priority'), choices=Story.PRIORITY_CHOICES)
	test_text = forms.CharField(label = mark_safe('Acceptance tests'), widget=forms.Textarea, error_messages=required_error)
	
	class Meta:
		model = Story
		fields = ('project_name', 'story_name', 'text', 'bussines_value', 'priority', 'test_text', )
		
	def clean_story_name(self):
		story_name_new = self.cleaned_data['story_name']
		project_name_id = self.cleaned_data['project_name']
		
		#covering with the other story name
		covering = Story.objects.filter(story_name = story_name_new, project_name = project_name_id)
					
		if len(covering) > 0:
			if not story_name_new == covering[0].story_name:
				raise ValidationError("Story with same name already exists.")
				return
		
		return story_name_new
		
class ProjectEditForm(forms.ModelForm):
	
	project_name =  forms.CharField(label = mark_safe(u'Project name'),max_length=50, error_messages=required_error)
	project_owner =  forms.ModelChoiceField(label = mark_safe(u'Product owner'),queryset=User.objects.all().order_by('username'),error_messages=required_error)
	scrum_master = forms.ModelChoiceField(label = mark_safe(u'Scrum master'),queryset=User.objects.all().order_by('username'),error_messages=required_error)
	team = forms.ModelMultipleChoiceField(widget=forms.HiddenInput(),queryset=User.objects.none(), required=False)
	
	
	#validate if name already taken under other roles
	def clean_scrum_master(self):
		scrum_master = self.cleaned_data['scrum_master']
		try:
			project_owner = self.cleaned_data['project_owner']
		except KeyError:
			return scrum_master
		
		if scrum_master==project_owner:
			raise ValidationError("Role "+str(scrum_master)+" is already taken.")
			return
		return scrum_master
	
		
	class Meta:
		model = Project
	
class TaskForm (forms.ModelForm):
	
	story = forms.ModelChoiceField(widget=forms.HiddenInput(),queryset=Story.objects.all(), required=False)
	duratino = forms.DecimalField(max_digits=4, decimal_places=1, label = mark_safe(u'Planned duration'), error_messages=velocity_error, validators=[MinValueValidator(
		Decimal('0.01')
		
			)])
	
	status = forms.IntegerField (widget=forms.HiddenInput(), initial=0)
	worker = forms.ModelChoiceField(queryset=User.objects.all(), label = mark_safe('Member'), required = False)
	 
	
	def __init__(self, project_id,*args,**kwargs):
		super (TaskForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['worker'].queryset = Project.objects.get(id=project_id).team.order_by('username')
			
	
	class Meta:
		model = Task
		
class TaskEditForm (forms.ModelForm):
	
	story = forms.ModelChoiceField(widget=forms.HiddenInput(),queryset=Story.objects.all(), required=False)
	duratino = forms.FloatField(label = mark_safe(u'Planned duration'), error_messages=velocity_error, validators=[
		RegexValidator(
			regex='^(?!0*(\.0+)?$)(\d+|\d*\.\d+)$',
			message='Please enter a positive float number.',
			code='invalid_value'
		),
	]) 
	
	status = forms.IntegerField (widget=forms.HiddenInput(), initial=0)
	worker = forms.ModelChoiceField(queryset=User.objects.all(), label = mark_safe('Member'), required = False)
	 
	
	def __init__(self, project_id,*args,**kwargs):
		super (TaskEditForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['worker'].queryset = Project.objects.get(id=project_id).team.order_by('username')
			
	
	class Meta:
		model = Task

class Work_Time_Edit_Form (forms.ModelForm) :
	task = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Task.objects.all(), required = True)
	worker = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=User.objects.all(), required = True)
	day = forms.DateField(label = mark_safe(u'Day'))
	time = forms.DecimalField(max_digits=4, decimal_places=1, label = mark_safe(u'Working time (in hours)'), required=True)
	
	class Meta:
		model = Work_Time





