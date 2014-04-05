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
		#related to Project DON'T CHANGE!
		return self.user.username

class Project(models.Model):
   
    # The additional attributes we wish to include.
	project_name =  models.CharField(blank=False, max_length=50)
	project_owner =  models.ForeignKey(User, related_name='owner', blank=False)
	scrum_master = models.ForeignKey(User, related_name='master', blank=False)
	team = models.ManyToManyField(User, blank=False)
	

    # Override the __unicode__() method to return out something meaningful!
	def __unicode__(self):
		# do not change, related to sprint
		return str(self.id)

class Sprint(models.Model):
	project_name = models.ForeignKey(Project)
	start_date = models.DateField(blank=False)
	finish_date = models.DateField(blank=False)
	velocity = models.IntegerField(blank=False)

	def __unicode__(self):
		return str(self.project_name)


class Story (models.Model):
	project_name = models.ForeignKey(Project)
	story_name = models.CharField(blank=False, max_length=100)
	text = models.TextField(blank=False, max_length=1000)
	bussines_value = models.IntegerField(blank=False)
	
	PRIORITY_CHOICES = (
        ('must have', 'must have'),
        ('could have', 'could have'),
        ('should have', 'should have'),
        ('won\'t have this time', 'won\'t have this time'),
    )
    
	priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, null=True, default='must have', blank=False)
	test_text = models.TextField(blank=False, max_length=1000)
	
	def __unicode__(self):
		return self.story_name
		




