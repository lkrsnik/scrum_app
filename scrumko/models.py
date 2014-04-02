from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
	user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    
	picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
	def __unicode__(self):
		return self.user.username

class Project(models.Model):
   
    # The additional attributes we wish to include.
    
	poject_name =  models.CharField(blank=False, max_length=50)
	project_owner =  models.ForeignKey(User, related_name='owner')
	scrum_master = models.ForeignKey(User, related_name='master')
	team = models.ManyToManyField(User)
	

    # Override the __unicode__() method to return out something meaningful!
	def __unicode__(self):
		return self.project.project_name


	




class Sprint(models.Model):
	project_name = models.ForeignKey(Project)
	start_date = models.DateField(blank=False)
	finish_date = models.DateField(blank=False)
	velocity = models.IntegerField(blank=False)

	def __unicode__(self):
		return self.sprint.project_name
