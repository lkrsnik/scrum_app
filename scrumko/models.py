from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime
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
	team = models.ManyToManyField(User, blank=True)
	

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
	estimate = models.DecimalField(default=0, max_digits=3, decimal_places=1)
	status = models.BooleanField(default=False) #True for finished
	
	def __unicode__(self):
		# do not change related to Poker
		return str(self.id)
		
class Poker (models.Model):
	project = models.ForeignKey(Project)
	story = models.ForeignKey(Story)
	active = models.BooleanField()
	
class Poker_estimates (models.Model):
	poker = models.ForeignKey(Poker)
	user = models.ForeignKey(User)
	estimate = models.DecimalField(max_digits=3, decimal_places=1)

class StoryNotification (models.Model):
	notification = models.CharField(max_length=1000)
	story = models.ForeignKey(Story)
	
class NotificationPermission (models.Model):
	permission = models.BooleanField()
	project = models.ForeignKey(Project)
		
class Story_Sprint (models.Model):
	story = models.ForeignKey(Story)
	sprint = models.ForeignKey(Sprint)

class Task (models.Model):
	story = models.ForeignKey (Story)
	text = models.CharField(max_length=1000, blank=False)
	duratino = models.DecimalField(max_digits=4, decimal_places=2, blank=False)
	worker = models.ForeignKey(User, blank=True, null=True)
	status = models.IntegerField(default=0)
		
class Work_Time (models.Model): 
	task = models.ForeignKey (Task)
	worker = models.ForeignKey(User)
	day = models.DateField(blank=False)
	time = models.DecimalField(max_digits=4, decimal_places=2, blank=False)
	
class Remaining (models.Model): 
	task = models.ForeignKey (Task)
	day = models.DateField(blank=False)
	time = models.DecimalField(max_digits=4, decimal_places=2, blank=False)

	
class Post (models.Model):
	project = models.ForeignKey(Project)
	poster = models.ForeignKey(User)
	post_time = models.DateTimeField(auto_now_add=True)
	content = models.CharField(max_length=1000, blank=False)
	
class Post_Comment (models.Model):
	post = models.ForeignKey(Post)
	comment_time = models.DateTimeField(auto_now_add=True)
	commenter = models.ForeignKey(User)
	comment = models.CharField(max_length=1000, blank=False)
	
class Documentation (models.Model):
	project = models.ForeignKey(Project)
	documentation_text = models.TextField(blank=True)



