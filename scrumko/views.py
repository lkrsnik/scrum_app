from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from scrumko.forms import UserForm, UserProfileForm, SprintCreateForm, ProjectCreateForm, StoryForm, ProjectEditForm, UserEditForm, NotificationPermissionForm, StoryEditForm, SprintEditForm, UserOrientedEditForm, TaskEditForm, Work_Time_Edit_Form
from scrumko.forms import TaskForm
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models import Min
from datetime import date, timedelta as td

from datetime import date, datetime
import datetime
from django.db.models import Sum

from scrumko.models import User
from scrumko.models import UserProfile, Task, Story_Sprint, Remaining
from scrumko.models import Sprint, Project, Story, Poker, Poker_estimates, NotificationPermission, StoryNotification, Work_Time, Post, Post_Comment, Documentation

from decimal import Decimal

import json
import decimal
#from scrumko.forms import UserForm, UserProfileForm

#from django.core.serializers.json import DjangoJSONEncoder



@ensure_csrf_cookie

@login_required
def home(request):
	
	# get current user
	current_user = request.user.id
	
	
	# Request the context of the request.
   	context = RequestContext(request)
        	
	# Project choose
	
	project_info = Project.objects.filter(Q(scrum_master__id = current_user) | Q(project_owner = current_user) | Q(team__id = current_user)).distinct()
	context_dict = {"project_detail" : project_info}
	
	# if user choose project, save this project id and name	
	if int(request.GET.get('project_id', '0'))>0:
		request.session['selected_project'] = int(request.GET.get('project_id', '0'))
		request.session['project_name'] = request.GET.get('name', '')
	# if project not choose
	else:
		if not request.session.get('selected_project'):
			# on begining select first project		
			# if exsist any project
			if len (project_info) > 0:
				pr = project_info[0]
				request.session['selected_project'] = pr.id
				request.session['project_name'] = pr.project_name
			else:	
				request.session['selected_project'] = 0
				request.session['project_name'] = ''
	
	# get information what roles user has on curent project
	selected_project_id = request.session['selected_project']
	is_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	is_project_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	# Construct a dictionary to pass to the template engine as its context.
	is_team_member = Project.objects.filter (team__id = current_user, id = selected_project_id).exists();
	
	context_dict.update( {'is_project_owner':is_project_owner, 'is_owner':is_owner, 'is_scrum_master': is_scrum_master, 'is_team_memeber' : is_team_member});	
				
	return render_to_response('scrumko/home.html', context_dict, context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def register(request):
    
	context = RequestContext(request)
	registered = False
	if request.method == 'POST':
  		user_form = UserForm(data=request.POST)
  		profile_form = UserProfileForm(data=request.POST)
		
		if user_form.is_valid() and profile_form.is_valid():	    
			user = user_form.save()	    
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
		else:
			print user_form.errors, profile_form.errors
			return render_to_response('scrumko/register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, context)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	return render_to_response('scrumko/register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, context)

def index(request):
    # Like before, obtain the context for the user's request.
	context = RequestContext(request)
	success=True;
    # If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
		username = request.POST['username']
		password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
		if user is not None:
            # Is the account active? It could have been disabled.
			if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
				login(request, user)
				
				request.session['selected_project'] = 0
				request.session['project_name'] = ''
				
				addprojecttosession (request)	
				
				return HttpResponseRedirect('/scrumko/home/')
			else:
                # An inactive account was used - no logging in!
				success=False;
				return HttpResponse("Your Scrumko account is disabled.")
		else:
            # Bad login details were provided. So we can't log the user in.
			print "Invalid login details: {0}, {1}".format(username, password)
			success=False;
			return render_to_response('scrumko/index.html', {'success': success}, context)
            #return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
	else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
		return render_to_response('scrumko/index.html', {'success': success}, context)

# this function add project in session

def addprojecttosession (request):
	# get all user projects and add it to session
	current_user = request.user.id
	project_info = Project.objects.filter(Q(scrum_master__id = current_user) | Q(project_owner__id = current_user) | Q(team__id = current_user)).distinct()
		
	# change this qs in array
	projects = []
	
	for pr in project_info:
		role = "as "
		if pr.scrum_master.id == current_user:
			role += "Scrum master"						
			role += ", " if pr.project_owner.id == current_user or pr.team.filter (id = current_user).exists() else " " 
			
		if pr.project_owner.id == current_user:
			role += "Project owner"
			role += ", " if pr.team.filter (id = current_user).exists() else " " 
			
		if pr.team.filter (id = current_user).exists():
			role += "Team member"
							
		d = [pr.project_name, pr.id, role]
		projects.append(d)
	
	request.session['project'] = projects


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
	
	request.session['selected_project'] = 0
	request.session['project_name'] = ''
	
	# Since we know the user is logged in, we can now just log them out.
	logout(request)

	# Take the user back to the homepage.
	return HttpResponseRedirect('/scrumko/')

@login_required
def productbacklog(request):
	context = RequestContext(request)
	
	if request.session['selected_project'] == 0:
		return render_to_response ('scrumko/noprojectselected.html', {}, context)
	
	allStories = Story.objects.filter(project_name__id=request.session['selected_project'], status = False)
	
	current_user = request.user.id
	selected_project_id = request.session['selected_project']
	is_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	note_permission = NotificationPermission.objects.get(project__id=selected_project_id)
	note_permission = note_permission.permission
	
	allNotifications = StoryNotification.objects.filter(story__project_name__id = selected_project_id)	
	addStorytoSprint = Story_Sprint.objects.filter(story__project_name__id = selected_project_id)
	addStorytoFinished = Story.objects.filter(project_name__id = selected_project_id)

	
	# get story sprint data for current project where story in current sprint
	story_sp = Story_Sprint.objects.filter(story__project_name__id = selected_project_id, sprint = current_sprint(request))
		
	# stories in sprint
	stroyinsprint = Story.objects.filter(project_name__id=request.session['selected_project'], id__in = story_sp.values_list('story_id', flat=True), status = False)
	
	stspnew = []
	
	for story in stroyinsprint:
		# check if not task finished
		allfinished = Task.objects.filter (story = story, status = 2)
		alltasks_st = Task.objects.filter (story = story)
		
		can_end = len(allfinished) > 0 and len (allfinished) == len (alltasks_st)
		stspnew.append ([story, can_end])		
	
	# stories not in sprint
	stroynotinsprint = Story.objects.filter(project_name__id=request.session['selected_project'],  status = False).exclude(id__in = story_sp.values_list('story_id', flat=True))
		
	# check if stprint exsist
	sprint_exsist = not current_sprint (request) == None;
	
	return render_to_response('scrumko/productbacklog.html', {'addStorytoFinished': addStorytoFinished,'addStorytoSprint': addStorytoSprint, 'allNotifications': allNotifications, 'note_permission': note_permission, 'stroyinsprint': stspnew, 'stroynotinsprint': stroynotinsprint, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master, 'sprint_exsist': sprint_exsist}, context)

def productbacklog_fin(request):
	context = RequestContext(request)
	
	if request.session['selected_project'] == 0:
		return render_to_response ('scrumko/noprojectselected.html', {}, context)
	
	# get all stories to show
	allStories = Story.objects.filter(project_name__id=request.session['selected_project'], status = True)
	
	current_user = request.user.id
	selected_project_id = request.session['selected_project']
	is_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	note_permission = NotificationPermission.objects.get(project__id=selected_project_id)
	note_permission = note_permission.permission
	
	allNotifications = StoryNotification.objects.filter(story__project_name__id = selected_project_id)
	
	return render_to_response('scrumko/productbacklog_fin.html', {'allNotifications': allNotifications, 'note_permission': note_permission, 'allStories': allStories, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master}, context)

def current_sprint(request):
	sprint = Sprint.objects.filter(project_name__id = request.session['selected_project'], start_date__lte = date.today(), finish_date__gte = date.today())
	
	if len (sprint ) == 0:
		return None
	else:
		return sprint[0]
		
@login_required
def sprintbacklog(request):
	this_sprint=current_sprint(request)
	if this_sprint!=None:
		allStories = Story_Sprint.objects.filter(sprint__id = current_sprint(request).id)
	else:
		allStories = None
	allTasks=Task.objects.all();
	
	context = RequestContext(request)

	if request.session['selected_project'] == 0:
		return render_to_response ('scrumko/noprojectselected.html', {}, context)

	#allStories = Story.objects.filter(project_name__id=request.session['selected_project'])
	
	current_user = request.user.id
	selected_project_id = request.session['selected_project']
	is_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	note_permission = NotificationPermission.objects.get(project__id=selected_project_id)
	note_permission = note_permission.permission
	
	allNotifications = StoryNotification.objects.filter(story__project_name__id = selected_project_id)
	addStorytoFinished2 = Story.objects.filter(project_name__id = selected_project_id)
	
	status = int(request.GET.get('accept', '0'))
	releasing = int(request.GET.get('release', '0'))
	if status > 0:
		taskid = int(request.GET.get('task', '0'))
		task = Task.objects.get(id=taskid);
		task.status=1;
		this_user=User.objects.get(id=current_user)
		task.worker=this_user
		task.save()		
	if releasing > 0:
		taskid = int(request.GET.get('task', '0'))
		task = Task.objects.get(id=taskid);
		task.status=0;
		task.worker=None
		task.save()
	
	#########################################
	# PG code here...						#
	#########################################
	
	#add previous all task in alltasks1
	alltasks1= allTasks	
	
	# create 2d table allTasks
	allTsaks2 = [[0 for x in range(3)] for x in range(len(alltasks1))]
	
	for i in range (len(alltasks1)):
		# get remaining for each task
		remaining = Remaining.objects.filter (task = alltasks1[i])
		
		allTsaks2[i][1] = remaining[len(remaining)-1].time
		allTsaks2[i][0] = alltasks1[i]
		
	#########################################
	#########################################
	
	return render_to_response('scrumko/sprintbacklog.html', {'addStorytoFinished2': addStorytoFinished2, 'allNotifications': allNotifications, 'note_permission': note_permission, 'allStories': allStories, 'allTasks': allTsaks2, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master}, context)

	
@login_required
def addstorytosprint(request, id):
	storyinsprint = False
	# get current user
	current_user = request.user.id
	
	# get selected project
	user_project =  Project.objects.filter(scrum_master__id = current_user, id = request.session['selected_project'])
	
	# redirect back if user has not permision	
	if len (user_project) == 0:	
		return HttpResponseRedirect('/scrumko/home')
	
	# check if story sprint exsist
	current_sprintek = current_sprint(request)
	
	if (current_sprintek) is None:
		return HttpResponseRedirect('/scrumko/home/')
	
	current_story = Story.objects.filter(id = id)

	# if current story is in current sprint
	sp_st = Story_Sprint.objects.filter(story = current_story, sprint = current_sprintek)
	
	if len (sp_st) > 0:
		
		return HttpResponseRedirect('/scrumko/home')
	else:
		
		if not current_sprintek or len(current_story) == 0:	
			return HttpResponseRedirect('/scrumko/home')
		else:	
			
			storyinsprint = True
		
			context = RequestContext(request)
			add = Story_Sprint.objects.create(sprint=current_sprintek, story = current_story[0])
			
			return HttpResponseRedirect("/scrumko/productbacklog")	
			
@login_required
def sprintcreate(request):
	# check permision to form and
	# project permision check
	current_user = request.user.id
	user_project =  Project.objects.filter(scrum_master__id = current_user, id = request.session['selected_project'])
	if len(user_project) == 0:
		return HttpResponseRedirect("/scrumko/home/")
	
	# set id of project to hidden input field
	r = user_project[0]

	# get context
	context = RequestContext(request)    
	
	# variable to check if sprint created
	registered = False
   
	if request.method == 'POST':
  		# get form inputs
  		sprint_form = SprintCreateForm(data=request.POST)

        # If the forms is valid...
		if sprint_form.is_valid():
			
            # Save the user's form data to the database.
			sprint = sprint_form.save()
			sprint.save()
			           
            # Update our variable to tell the template registration was successful.
			registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
		else:
			print sprint_form.errors
			return render_to_response('scrumko/sprintcreate.html',{'sprint_form': sprint_form, 'registered': registered}, context)
	
	sprint_form = SprintCreateForm(initial={'project_name': r.id})		
		
    # Render the template depending on the context.
	return render_to_response('scrumko/sprintcreate.html',{'sprint_form': sprint_form, 'registered': registered}, context)

@login_required
#@transaction.atomic

def maintainsprint(request):
	context = RequestContext(request)
	sprint_info = Sprint.objects.filter(project_name__id=request.session['selected_project'])
		
	current = [[0 for x in range (2)] for x in range (len (sprint_info))]	
	for i in range (len (sprint_info)):
		
		current[i][0] = sprint_info[i]
		if sprint_info[i].start_date <= date.today():
			current[i][1] = True
		else:
			current[i][1] = False
	
	sprint_data = { 'current' : current}
    # Render the template depending on the context.
	return render_to_response('scrumko/maintainsprint.html', sprint_data, context)
	
def sprintedit(request, id):
	already_exist_message = ""
	context = RequestContext(request)
	
	registered = False	
	if request.method == 'POST':
		sprint_info =Sprint.objects.filter(id =id)
		r= sprint_info[0]
	
		oldstart_date = r.start_date
		oldfinish_date = r.finish_date
		
		r.start_date = '1900-01-01'
		r.finish_date = '1900-01-01'
		r.save()
		
		sprint_form = SprintEditForm(data=request.POST)		
		
        # If the two forms are valid...
		if sprint_form.is_valid():
			#change=True;
			 
			start_date = request.POST['start_date'] 
			finish_date = request.POST['finish_date'] 
			velocity = request.POST['velocity']
			r.start_date=datetime.datetime.strptime(start_date, '%m/%d/%Y')				
			r.finish_date=datetime.datetime.strptime(finish_date, '%m/%d/%Y')
			r.velocity=velocity
			r.save();
			registered=True
		else:
			r.start_date = oldstart_date
			r.finish_date = oldfinish_date
			r.save()
			
			print sprint_form.errors
			return render_to_response('scrumko/sprintedit.html',{'sprint_form': sprint_form, 'registered': registered, 'sprint_id': id}, context)

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		sprint_info =Sprint.objects.filter(id =id)
		r= sprint_info[0]
	
	
	#start_date_d = datetime.datetime.strptime(r.start_date, '%Y-%m-%d')

	sprint_form = SprintEditForm(initial={'project_name': r.project_name, 'start_date': r.start_date.strftime('%m/%d/%Y'), 'finish_date': r.finish_date.strftime('%m/%d/%Y'), 'velocity': r.velocity})
	# Render the template depending on the context.
	return render_to_response('scrumko/sprintedit.html',{'sprint_form': sprint_form, 'registered': registered, 'sprint_id': id}, context)	

def sprintdelete(request, sprint_id):
	context = RequestContext(request)
	sprint_info = Sprint.objects.get(id=sprint_id).delete()
	return HttpResponseRedirect("/scrumko/maintainsprint")
		
def projectcreate(request):

    # Like before, get the request's context.
	
	context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
	registered = False
	all_members = "";
	all_options=User.objects.all().order_by('username')
    # If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
		
  		project_form = ProjectCreateForm(data=request.POST)
  		notification_form = NotificationPermissionForm(data=request.POST)
  		all_members = request.POST.get('all_members')
		
		
        # If the two forms are valid...
		if project_form.is_valid() and notification_form.is_valid():
						
            # Save the user's form data to the database.
			scrum_master=User.objects.filter(id = int(request.POST.get('scrum_master')))
			scrum_master.update(is_staff = True)

			
			
			for member in scrum_master:
				member.save()

			project = project_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.		
			project.save()
			
			# check if is scrum master or team member
           
            # Update our variable to tell the template registration was successful.
			registered = True

			project_team=Project.objects.all()
			max = int(0)
			for proj in project_team:
				if max < int(proj.id):
					max = int(proj.id)

			project_test=Project.objects.filter(id = int(max))
			for team_member in all_members.split(' '):
				member_test=User.objects.filter(username = team_member)
				project_test[0].team.add(int(member_test[0].id))
	
			all_members=""
			
			
			notification_permission = notification_form.save(commit=False)
			notification_permission.project = project_test[0]
			notification_permission.permission=request.POST.get('permission', False)
			notification_permission.save()
		
			addprojecttosession (request)
		
		else:
			print project_form.errors
			return render_to_response('scrumko/projectcreate.html',{'project_form': project_form, 'notification_form': notification_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options}, context)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
	
	project_form = ProjectCreateForm()
	notification_form= NotificationPermissionForm(initial={'permission':False})	
		
    # Render the template depending on the context.
	return render_to_response('scrumko/projectcreate.html',{'project_form': project_form, 'notification_form': notification_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options}, context)
def maintainuser(request):
	context = RequestContext(request)
	user_info = User.objects.all()
	user_data = {"user_detail" : user_info}

	
    # Render the template depending on the context.
	return render_to_response('scrumko/maintainuser.html',user_data, context)

def userdelete(request, id):
	context = RequestContext(request)
	user_info = User.objects.get(id=id).delete()
	return HttpResponseRedirect("/scrumko/maintainuser")		
	


def maintainproject(request):
	context = RequestContext(request)
	project_info = Project.objects.all()
	project_data = {"project_detail" : project_info}	
    # Render the template depending on the context.
	return render_to_response('scrumko/maintainproject.html', project_data, context)
	
def projectdelete(request, id):
	context = RequestContext(request)
	projecr_info = Project.objects.get(id=id).delete()
	
	# refresh project array
	addprojecttosession (request)
	
	return HttpResponseRedirect("/scrumko/maintainproject")	

@login_required
def editproject(request):
	already_exist_message = ""
	context = RequestContext(request)
	# Render the template depending on the context.
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
   
	registered = False
	all_members = "";
	all_options=User.objects.all().order_by('username')
	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		projectid = request.POST['proj_id']
		project_info = Project.objects.filter(id = projectid)
		r= project_info[0]
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
		
		project_form = ProjectEditForm(data=request.POST)
		notification_form = NotificationPermissionForm(data=request.POST)
		all_members = request.POST.get('all_members')
		
		
        # If the two forms are valid...
		if project_form.is_valid() and notification_form.is_valid():
			change=True;
			scrum_master = request.POST['scrum_master']
			project_owner = request.POST['project_owner']
			project_name = request.POST['project_name']
			already_exist=Project.objects.filter(project_name=project_name)
			if len(already_exist)>0:
				already_exist=already_exist[0]
				if not already_exist.id == r.id:
					change=False;
					already_exist_message = "Username already exists!"
					is_scrum_master = len (Project.objects.filter(scrum_master__id = request.user.id, id = projectid)) > 0
					return render_to_response('scrumko/editproject.html',{'is_scrum_master': is_scrum_master, 'notification_form': notification_form, 'already_exist_message': already_exist_message, 'project_form': project_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options, "project_detail" : project_info}, context)
			if(change):
				r.scrum_master=User.objects.get(id=scrum_master)
				r.project_owner=User.objects.get(id=project_owner)			
				r.project_name=project_name
				r.save();
				for team_member in r.team.all():	
					project_info[0].team.remove(team_member)
					
				
				for team_member in all_members.split(' '):
					member_test=User.objects.filter(username = team_member)
					project_info[0].team.add(int(member_test[0].id))	
				
				notification_perm=NotificationPermission.objects.get(project__id=project_info[0].id)
				
				notification_perm.permission=request.POST.get('permission', False)
				notification_perm.save()

				registered = True	
				all_members=""
				
				addprojecttosession (request)

		else:
			print project_form.errors
			is_scrum_master = len (Project.objects.filter(scrum_master__id = request.user.id, id = projectid)) > 0
			return render_to_response('scrumko/editproject.html',{'is_scrum_master': is_scrum_master, 'notification_form': notification_form, 'already_exist_message': already_exist_message, 'project_form': project_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options, "project_detail" : project_info}, context)

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		projectid = int(request.GET.get('id', '0'))
		project_info = Project.objects.filter(id = projectid)
		r = project_info[0]
	all_members=""
	for team_member in r.team.all():
		
		team_member=team_member.username
		all_members=all_members+" "+team_member
		

	is_scrum_master = len (Project.objects.filter(scrum_master__id = request.user.id, id = projectid)) > 0
	notif_perm=NotificationPermission.objects.filter(project__id=r.id)
	project_form = ProjectEditForm(initial={'project_name': r.project_name, 'project_owner': r.project_owner, 'scrum_master': r.scrum_master, 'team': r.team})
	notification_form = NotificationPermissionForm(initial={'permission': notif_perm[0].permission})
	# Render the template depending on the context.
	return render_to_response('scrumko/editproject.html',{'is_scrum_master': is_scrum_master, 'notification_form': notification_form, 'already_exist_message': already_exist_message, 'project_form': project_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options, "project_detail" : project_info}, context)
	

@login_required

def storycreate(request):
    
    # get current user
	current_user = request.user.id
	
	# check on which project is this user owner or scrum master
	user_project_master =  Project.objects.filter(scrum_master__id = current_user, id = request.session['selected_project'])
	user_project_owner =  Project.objects.filter(project_owner__id = current_user, id = request.session['selected_project'])
    
    # check if user is scrum master or owner 
    # if not redirect (he has no permision to this site)
	if len (user_project_master) == 0 and len (user_project_owner) == 0:
		return HttpResponseRedirect("/scrumko/home")
	       
	context = RequestContext(request)
	registered = False
	if request.method == 'POST':
		story_form = StoryForm(data=request.POST)
  		
  				
		if story_form.is_valid():	    
			story = story_form.save()	    
									
				
			registered = True
		else:
			print story_form.errors
			return render_to_response('scrumko/storycreate.html',{'story_form': story_form, 'registered': registered}, context)
		
	# take project where user is scrum master or owner
	if len (user_project_master) > 0:
		r = user_project_master[0]
	elif len (user_project_owner) > 0:
		r = user_project_owner[0]
	
	# fill hidden with id of project
	story_form = StoryForm(initial={'project_name': r.id})
	
	return render_to_response('scrumko/storycreate.html',{'story_form': story_form, 'registered': registered}, context)

@login_required
def storyedit(request, id):
	# get current user
	current_user = request.user.id
	
	# check on which project is this user owner or scrum master
	user_project_master =  Project.objects.filter(scrum_master__id = current_user, id = request.session['selected_project'])
	user_project_owner =  Project.objects.filter(project_owner__id = current_user, id = request.session['selected_project'])
    
    # check if user is scrum master or owner 
    # if not redirect (he has no permision to this site)
	if len (user_project_master) == 0 and len (user_project_owner) == 0:
		return HttpResponseRedirect("/scrumko/home")
	       
	context = RequestContext(request)
	registered = False
	story_info = Story.objects.filter(id = id)
	r = story_info[0]
	if request.method == 'POST':
		story_form = StoryEditForm(data=request.POST)
  		
  				
		if story_form.is_valid():
			already_exist=Story.objects.filter(project_name=request.POST['project_name'],story_name=request.POST['story_name'])
			
			if len(already_exist)>0 and not already_exist[0].id == r.id:
				
				already_exist_message = "* Username already exists!"
				return render_to_response('scrumko/storyedit.html',{'already_exist_message':already_exist_message, 'story_form': story_form, 'registered': registered,'story_id': id}, context)
			else:    
				r.story_name=request.POST['story_name']
				r.text=request.POST['text']
				r.bussines_value=request.POST['bussines_value']	
				r.priority=request.POST['priority']	
				r.test_text=request.POST['test_text']
				#r.project_name=User.objects.get(id=project_owner)	
				r.save();
				registered = True
		else:
			print story_form.errors
			return render_to_response('scrumko/storyedit.html',{'story_form': story_form, 'registered': registered,'story_id': id}, context)
	
	
		
		
		
	story_form = StoryEditForm(initial={'project_name': r.project_name, 'story_name': r.story_name, 'text': r.text, 'bussines_value': r.bussines_value, 'priority': r.priority, 'test_text': r.test_text})
	
	return render_to_response('scrumko/storyedit.html',{'story_form': story_form, 'registered': registered,'story_id': id}, context)

def storydelete(request, id):
	context = RequestContext(request)
	Story.objects.get(id=id).delete()
	return HttpResponseRedirect("/scrumko/productbacklog")	
	
def edit(request):
	context = RequestContext(request)	
	registered = False
	
	if request.method == 'POST':
		userid = request.POST['us_id']
		project_info = User.objects.filter(id = userid)
		r= project_info[0]
		
		oldusername = r.username
		
		r.username = ""
		r.save()
        
		user_form = UserEditForm(data=request.POST)
		
		if user_form.is_valid():			
			username = request.POST['username']
			email = request.POST['email']
			is_superuser = request.POST.get('is_superuser', False)
			first_name = request.POST['first_name']
			last_name = request.POST['last_name']
			password = request.POST['password']
			r.username = username
			r.email = email			
			r.is_superuser = is_superuser
			r.first_name = first_name
			r.last_name = last_name
			if not len (password) == 0:

				r.set_password(password)
			r.save(); 
			
			registered = True	
			
		else:
			
			r.username = oldusername
			r.save()
			
			print user_form.errors		
			return render_to_response('scrumko/edit.html',{'user_form': user_form, 'registered': registered, "project_detail" : project_info}, context)
	
	else:
		userid = int(request.GET.get('id', '0'))
		project_info = User.objects.filter(id = userid)
		r = project_info[0]	
	user_form = UserEditForm(initial={'username': r.username, 'email': r.email, 'is_superuser': r.is_superuser, 'first_name': r.first_name, 'last_name': r.last_name, 'password': r.password, 'password2': r.password })
	
	return render_to_response('scrumko/edit.html',{	'user_form': user_form, 'registered': registered, 'project_detail' : project_info}, context)

@login_required
def editmyprofile(request,id):
	context = RequestContext(request)	
	registered = False
	print id
	
	if request.method == 'POST':
		#userid = request.POST['us_id']
		project_info = User.objects.filter(id = id)
		r= project_info[0]
        
		oldusername = r.username
		
		r.username = ""
		r.save()
		
		user_form = UserOrientedEditForm(data=request.POST)
		
		if user_form.is_valid():				
			username = request.POST['username']
			email = request.POST['email']
			#is_superuser = request.POST['is_superuser']
			first_name = request.POST['first_name']
			last_name = request.POST['last_name']
			password = request.POST['password']
			r.username = username
			r.email = email			
			#r.is_superuser = is_superuser
			r.first_name = first_name
			r.last_name = last_name
			if not len (password) == 0:

				r.set_password(password)
			r.save(); 
			
			registered = True	
			
		else:
			r.username = oldusername
			r.save()
			print user_form.errors		
			return render_to_response('scrumko/editmyprofile.html',{'user_form': user_form, 'registered': registered, "project_detail" : project_info}, context)
	
	else:
		#userid = int(request.GET.get('id', '0'))
		project_info = User.objects.filter(id = id)
		r = project_info[0]	
	user_form = UserOrientedEditForm(initial={'username': r.username, 'email': r.email, 'is_superuser': r.is_superuser, 'first_name': r.first_name, 'last_name': r.last_name, 'password': r.password, 'password2': r.password })
	
	return render_to_response('scrumko/editmyprofile.html',{'user_form': user_form, 'registered': registered, 'project_detail' : project_info}, context)
	
@login_required	
def startpoker(request, user_story_id):
		
	# get current user
	current_user = request.user.id
	
	# get selected project
	user_project =  Project.objects.filter(scrum_master__id = current_user, id = request.session['selected_project'])
	
	# redirect back if user has not permision	
	if len (user_project) == 0:	
		return HttpResponseRedirect('/scrumko/home')
	
	# get user story
	story = Story.objects.filter(id = user_story_id, project_name = user_project[0])
	
	# redirect back if story doesent exsist	
	if len (story) == 0:
		return HttpResponseRedirect('/scrumko/home')
		
	## check if everyone voted in previous poker
	# get active stoy on planing poker
	active_poker = Poker.objects.filter (project__id = request.session['selected_project'], active = True, story = story)
	
	if len (active_poker) > 0:
		
		# all users on project
		team = Project.objects.get (id = request.session['selected_project']).team.all()
		scrum_m = Project.objects.get (id = request.session['selected_project']).scrum_master
				
		# check if scrum master in team 
		inteam = 1
		for t in team:
			if t.id == scrum_m.id:
				inteam = 0
		
		numofmember = len (team) + inteam
		
		# get all estimates in poker
		estimates_p = Poker_estimates.objects.filter (poker = active_poker[0])
		
		if not len (estimates_p) == numofmember:		
			return HttpResponseRedirect('/scrumko/poker')
		
	
	# close older stories
	older_opened = Poker.objects.filter(project=user_project[0], active = True)
	for pok in older_opened:
		pok.active = False
		pok.save()	

	# if everything ok start poker with writing it in database
	poker = Poker.objects.create(project=user_project[0], story = story[0], active = True)
		
	return HttpResponseRedirect('/scrumko/poker')

@login_required	
def poker (request):
	print "ncjasnfdasfdsnfkdasfjkldshfkjdshfkjdashjfkjhfkjdshfkdsjfkjdashfkjdshfkjdshfkjdshfkjdshfkjdashflkjashflkjdashfkjdashfkj"
	
	# get context
	context = RequestContext(request)
	
	# initialize dictionary to push content on page
	context_dict = {}
	
	# get active stoy on planing poker
	active_poker = Poker.objects.filter (project__id = request.session['selected_project'])
	
	
	## add data to dictionary
	
	# if not active poker, then writeout this
	if len (active_poker) == 0 :
		context_dict.update ({'story_text' : 'There is no active planning poker right now.'})
	
	#if data available write-out
	else:		
		active_poker = active_poker[len(active_poker) - 1]	
		# write data for descriptions
		story = active_poker.story
		context_dict.update ({'story_text' : story.text, 'story_test' : story.test_text, 'story_name' : story.story_name})
		
		# dict for table
		table_dict = {}		
			
	# get data for previous planigs
	return render_to_response('scrumko/planing_poker.html', context_dict, context)

# function used to find data for poker writeout	
def get_poker_data (project_id, story, current_user):
	# get all pokers
	pokers = Poker.objects.filter (project__id = project_id, story = story)
			
	# get all estimates on this story
	estimates = Poker_estimates.objects.filter (poker__project__id = project_id, poker__story = story)
	
	# get all users on this story
	users = estimates.values('user').distinct()
	users_value = []
	for user in users:
		users_value.append (User.objects.get (id = user['user']))
			
	# create 2D table of estimates planing poker
	estimate_value = [[0 for x in range (len (users)+2)] for x in range (len (pokers))]	
	
	# count empty for indexing
	emty_row_num = 0
	for i in range (len (pokers)):
		estimate_value[i][0] = i+1 - emty_row_num
		
		# calculating estimates average
		avg = 0
		num = 0
		
		for j in range (len (users)):
			res = Poker_estimates.objects.filter (poker = pokers[i], user__id = users[j]['user'])
			if len (res) == 0 or res[0].estimate == -1:
				estimate_value[i][j+1] = '-'
			else:
				estimate_value[i][j+1] = res[0].estimate 
				avg = avg + res[0].estimate 
				num = num + 1
			
		# row average
		if num == 0:
			# delete table row if empty
			estimate_value[i] = []
			emty_row_num = emty_row_num + 1			
		else:
			estimate_value[i][j+2] = '%.2f' % (avg / num)
			
	# check if last planing poker has no my submision
	my_last = Poker_estimates.objects.filter (poker = pokers[i], user__id = current_user)
	last_estimate = len (my_last ) == 0
		
	# delete last row if no my submision
	if last_estimate:
		estimate_value[i:i+1] = []
		
	if len (users) > 0:
		cell =  75 / len (users)
	else:
		cell = 0
		
	return {'estimate_value' : estimate_value, 'users_value' : users_value, 'last_round' : last_estimate, 'cellwidth' : cell	}

# function wich tell what to show in poker (eg. butttons and other)
def get_button_poker_data (project_id, story, current_user):
	# create dictionary
	button_dict = {}
		
	## is user scrum master
	
	# get selected project
	user =  Project.objects.filter(scrum_master__id = current_user, id = project_id)
	
	# check if scrum master
	if len (user) > 0:
		button_dict.update ({'scrummaster' : True })
	else:
		button_dict.update ({'scrummaster' : False })
	
	## story active?
	
	# get active stoy on planing poker
	active_poker = Poker.objects.filter (project__id = project_id, active = True)
	
	if len (active_poker) > 0:
		## check if everyone voted
		
		# all users on project
		team = Project.objects.get (id = project_id).team.all()
		scrum_m = Project.objects.get (id = project_id).scrum_master
				
		# check if scrum master in team 
		inteam = 1
		for t in team:
			if t.id == scrum_m.id:
				inteam = 0
		
		numofmember = len (team) + inteam
		
		# get all estimates in poker
		estimates_p = Poker_estimates.objects.filter (poker = active_poker[0])
		
		if len (estimates_p) >= numofmember:		
			button_dict.update ({'enableend' : True })
		else:
			button_dict.update ({'enableend' : False })
			
		button_dict.update ({'activeround' : True })
	else:
		button_dict.update ({'activeround' : False })
		button_dict.update ({'enableend' : False })

	## estimated from this user?
	
	# get estimates of this user for current active story
	estimates = Poker_estimates.objects.filter (poker__project__id = project_id, poker__active = True, user__id = current_user)
	
	# check if exsist
	
	if len (estimates) > 0 or len (active_poker) == 0:
		button_dict.update ({'estimates' : False })
		
	else:
		button_dict.update ({'estimates' : True })
		
	
	
	
	# return data from dict
	
	return button_dict

def poker_table (request):
	context = RequestContext(request)
	# get active stoy on planing poker
	active_poker = Poker.objects.filter (project__id = request.session['selected_project'])
	
	if len (active_poker) == 0:
		return_dict = {'table' : '', 'button' : '' }
		return HttpResponse(json.dumps(return_dict), content_type="application/json")
	
	# get last one
	active_poker = active_poker[len (active_poker) - 1]
	
	## poker table
	
	# write data for descriptions
	story = active_poker.story	
	
	poker_estimates = get_poker_data (request.session['selected_project'], story, request.user.id)
	table_dict =  poker_estimates
	
	# render teplate in string
	table_str = render_to_string('scrumko/planing_poker/table.html', table_dict, context)
	
	## buttons
	
	# get data from function
	button_data = get_button_poker_data (request.session['selected_project'], story, request.user.id)
	
	# render template
	button_str = render_to_string('scrumko/planing_poker/buttons.html', button_data, context)
	
	## story text
	
	context_dict =  ({'story_text' : story.text, 'story_test' : story.test_text, 'story_name' : story.story_name})
	
	# make dict to return with JSON
	return_dict = {'table' : table_str, 'button' : button_str }
	return_dict.update (context_dict)
	
	# return data to ajax call
	return HttpResponse(json.dumps(return_dict), content_type="application/json")

# function writeout estimation for project on current planing poker 	
def poker_estimate (request):
			
	# get user estimate
	# pass note with -1 database
	est = request.GET.get('estimate')
	if est == 'Pass':
		est = -1
	estimate = Decimal (est)
	
	# get active poker
	active_poker = Poker.objects.get (project__id = request.session['selected_project'], active = True)
	
	# get user
	user = request.user
	
	#check if est exsist
	estimate_model = Poker_estimates.objects.filter(poker = active_poker, user = user)
	if len (estimate_model) > 0:
		return HttpResponse("")
				
	Poker_estimates.objects.create(poker = active_poker, user = user, estimate = estimate)
	
	return HttpResponse("")
	
# function end round of planing poker
def poker_disactivate (request):
	
	active_poker = Poker.objects.get (project__id = request.session['selected_project'], active = True)
	
	active_poker.active = False
	active_poker.save()
	
	return HttpResponse("")	
	
# function use last estimate
def poker_uselast (request):
	# get last story
	data = Poker.objects.filter (project__id = request.session['selected_project'])
	story = data[len (data)-1].story
	
	# get all pokers on this story
	pokers = Poker.objects.filter (project__id = request.session['selected_project'], story = story)
	
	# iterate throught pokers and find first with one or more estimates
	for poker in reversed(pokers):
		# find all estimates
		estimates = Poker_estimates.objects.filter (poker = poker)
		
		if len (estimates) > 0:
			avg_e = calc_avg_est (estimates)
			story.estimate = avg_e
			story.save()
			 
			break

	# add to return that no estimate if not!!!!
	return HttpResponseRedirect("/scrumko/productbacklog")	
	
# function calculate avarage of estimates
def calc_avg_est (est):
	total = 0
	num  = 0
	for e in est:
		if e >= 0:
			total = total + e.estimate
			num = num + 1
		
	return total / num
	
	
# function start ne round of planing poker
def poker_activate (request):
	
	# user story to start new poker
	
	story = (Poker.objects.filter (project__id = request.session['selected_project']))
	story = story[len (story) - 1].story
	
	# get current user
	current_user = request.user.id
	
	# get selected project
	user_project =  Project.objects.filter(scrum_master__id = current_user, id = request.session['selected_project'])
	
	# redirect back if user has not permision	
	if len (user_project) == 0 or not story :	
		return HttpResponseRedirect('/scrumko/home')
	
	# close older stories
	older_opened = Poker.objects.filter(project=user_project[0], active = True)
	for pok in older_opened:
		pok.active = False
		pok.save()	

	# if everything ok start poker with writing it in database
	poker = Poker.objects.create(project=user_project[0], story = story, active = True)
	
	return HttpResponse("")	

# function changes estimation of story
def add_notification (request):
	storyid = request.POST["storyid1"];
		
	story1 = Story.objects.filter (id = storyid);
	
	note1=StoryNotification.objects.filter(story__id = storyid)
	if len (note1) > 0:
		note1[0].notification=request.POST["note"]
		note1[0].save()
	else:
		p = StoryNotification.objects.create(story=story1[0], notification=request.POST["note"])
	return HttpResponseRedirect('/scrumko/productbacklog/')# function changes estimation of story
# def add_notification (request):
	# storyid = request.POST["storyid1"];
		
	# story1 = Story.objects.filter (id = storyid);
	
	# note1=StoryNotification.objects.filter(story__id = storyid)
	# if len (note1) > 0:
		# note1[0].notification=request.POST["note"]
		# note1[0].save()
	# else:
		# p = StoryNotification.objects.create(story=story1[0], notification=request.POST["note"])
	# return HttpResponseRedirect('/scrumko/productbacklog/')
def add_notification1 (request):
	storyid = request.POST["storyid1"];
		
	story1 = Story.objects.filter (id = storyid);
	
	note1=StoryNotification.objects.filter(story__id = storyid)
	if len (note1) > 0:
		note1[0].notification=request.POST["note"]
		note1[0].save()
	else:
		p = StoryNotification.objects.create(story=story1[0], notification=request.POST["note"])
	return HttpResponseRedirect('/scrumko/sprintbacklog/')
def change_estimation (request):
	
	# get id where changing estimates
	storyid = request.POST["storyid"];
		
	# find story to change estimate
	story = Story.objects.filter (id = storyid);
	
	# check if this story exsist
	if len (story) > 0:
		# if ok repair value
		story[0].estimate = request.POST["estimation"];
		story[0].save();
	
	return HttpResponseRedirect('/scrumko/productbacklog/')
def change_estimation1 (request):
	
	# get id where changing estimates
	storyid = request.POST["storyid"];
		
	# find story to change estimate
	story = Story.objects.filter (id = storyid);
	
	# check if this story exsist
	if len (story) > 0:
		# if ok repair value
		story[0].estimate = request.POST["estimation"];
		story[0].save();
	
	return HttpResponseRedirect('/scrumko/sprintbacklog/')
def change_remaining (request):
	
	# get id where changing estimates
	taskid1 = request.POST["taskid1"]
		
	# find story to change estimate
	task = Task.objects.filter (id = taskid1)
	
	# check if this story exsist
	if len (task) > 0:
		# if ok add new remaining
		rem = request.POST["duration"]
		Remaining.objects.create (task = task[0], day = date.today(), time = rem)
	
	return HttpResponseRedirect('/scrumko/mytask/')
def taskcreate (request, id):
	
	context = RequestContext(request)
	success=False;
	context_dict = {};
	
	# check if story is in sprint
	st_sp = Story_Sprint.objects.filter(story__id = id, sprint__start_date__lte = date.today(), sprint__finish_date__gte = date.today())
	if len (st_sp) == 0:
		return HttpResponseRedirect('/scrumko/home/')
    
    # check if story finished
	sprint = Story.objects.filter(id = id, status = False)
	if len (sprint) == 0:
		return HttpResponseRedirect('/scrumko/home/')
    
	# get project id
	project_id = request.session['selected_project']
	context_dict['id'] = id
	
	# get all taskes and data for write out in papge
	tasks = Task.objects.filter (story__id = id)
	context_dict['tasks'] = tasks;	
	
	    
	if request.method == 'POST':
        
		task_form = TaskForm(project_id, data=request.POST)    
        
		if task_form.is_valid():
			task = task_form.save()			
			if task.worker == None:
				task.status = 0
			else:
				task.status = 3
			task.save()
			
			# add remaining time to remaining model
			Remaining.objects.create (task = task, day = date.today(), time = task.duratino)
						
			success=True;
		else:				
			print task_form.errors	
			context_dict ['success'] = success
			context_dict ['task_form'] = task_form	
			return render_to_response ('scrumko/taskcreate.html', context_dict, context)
    
	# get form and add to dict
	
	task_form = TaskForm(project_id, initial={'story': id}) 
	context_dict ['task_form'] = task_form
	context_dict ['success'] = success
       
	# render page
	return render_to_response ('scrumko/taskcreate.html', context_dict, context)

@login_required
def taskedit (request, id):
	
	context = RequestContext(request)
	success=False;
	context_dict = {};
	
	# get task and data for write out in papge
	this_task = Task.objects.get(id = id);
	context_dict['this_task'] = this_task
	# check if story is in sprint
	st_sp = Story_Sprint.objects.filter(story__id = this_task.story.id, sprint__start_date__lte = date.today(), sprint__finish_date__gte = date.today())
	if len (st_sp) == 0:
		return HttpResponseRedirect('/scrumko/home/')
    
    # check if story finished
	sprint = Story.objects.filter(id = this_task.story.id, status = False)
	if len (sprint) == 0:
		return HttpResponseRedirect('/scrumko/home/')
    
	# get project id
	project_id = request.session['selected_project']
	context_dict['id'] = this_task.story.id
	
	
	
	tasks = Task.objects.filter (story__id = this_task.story.id)
	context_dict['tasks'] = tasks;
	

	if request.method == 'POST':
        
		task_form = TaskEditForm(project_id, data=request.POST)    
        
		if task_form.is_valid():
			#task_form.save()
			this_task.text=request.POST['text']
			this_task.duratino=request.POST['duratino']
			if request.POST['worker'] != "":
				new_worker=User.objects.get(id = request.POST['worker'])
				if this_task.worker != new_worker:
					this_task.status=3
					this_task.worker = new_worker;
			else:
				this_task.status=0
				this_task.worker=None
			this_task.save();
			success=True;
		else:				
			print task_form.errors	
			context_dict ['success'] = success
			context_dict ['task_form'] = task_form	
			return render_to_response ('scrumko/taskedit.html', context_dict, context);
    
	# get form and add to dict
	task_form = TaskEditForm(project_id, initial={'story': this_task.story.id, 'text': this_task.text, 'duratino': this_task.duratino, 'worker': this_task.worker}) 
	context_dict ['task_form'] = task_form
	context_dict ['success'] = success
       
	   
	# render page
	return render_to_response ('scrumko/taskedit.html', context_dict, context);

def taskdelete(request, id):
	context = RequestContext(request)
	Task.objects.get(id=id).delete()
	return HttpResponseRedirect("/scrumko/sprintbacklog")
	
def taskdelete_createlist(request, id):
	context = RequestContext(request)
	storyid = Task.objects.get(id=id).story.id
		
	Task.objects.get(id=id).delete()
	return HttpResponseRedirect("/scrumko/taskcreate/" + str(storyid) + "/")
	
@login_required	
def mytask(request): 
	completing = int(request.GET.get('complete', '0'))
		
	insprint = True
	inday = True   
	error_time=""
	error_sprint=""
	update=False;
	notasks=True;
	current_user = request.user.id	
	this_sprint=current_sprint(request)
	context = RequestContext(request)
	
	if this_sprint!=None:
		allStories = Story_Sprint.objects.filter(sprint__id = current_sprint(request).id)
		notasks=False;
	else:
		# ce ni taskov, te vrze na home
		allStories = None;
		notasks=True;
		return render_to_response ('scrumko/notaskselected.html', {}, context)
	allTasks=Task.objects.filter(worker = current_user);
	stories = [];
	
	# if allTasks == None:
		 # return HttpResponseRedirect("/scrumko/sprintbacklog")
		
	for story in allStories:
		for task in allTasks:
			if task.story.id == story.story.id and task.status == 1:
				stories.append(story)
				break
		
	allStories=stories
	
	#########################################
	# PG code here...						#
	#########################################
	
	#add previous all task in alltasks1
	alltasks1= allTasks
	
	
	# create 2d table allTasks
	allTsaks2 = [[0 for x in range(3)] for x in range(len(alltasks1))]
	
	for i in range (len(alltasks1)):
		# get remaining for each task
		remaining = Remaining.objects.filter (task = alltasks1[i])
		workdone = Work_Time.objects.filter (task = alltasks1[i]).aggregate(Sum('time'))
		print (workdone )
		allTsaks2[i][2] = remaining[len(remaining)-1].time + (0 if workdone['time__sum']==None else workdone['time__sum'])			
		allTsaks2[i][1] = remaining[len(remaining)-1].time
		allTsaks2[i][0] = alltasks1[i]
		
	#########################################
	#########################################
	
	

	if request.session['selected_project'] == 0:
		return render_to_response ('scrumko/noprojectselected.html', {}, context)

	#allStories = Story.objects.filter(project_name__id=request.session['selected_project'])
	
	
	selected_project_id = request.session['selected_project']
	is_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	note_permission = NotificationPermission.objects.get(project__id=selected_project_id)
	note_permission = note_permission.permission
	
	allNotifications = StoryNotification.objects.filter(story__project_name__id = selected_project_id)

	
	#check if it is completeted
	if completing > 0:

		taskid = int(request.GET.get('task', '0'))
		task = Task.objects.get(id=taskid);
		task.status=2;
		task.duratino=0;
		#task.worker=None
		task.save()
		return HttpResponseRedirect("/scrumko/mytask")
	workTime = Work_Time.objects.filter(worker__id = current_user)
	work={}
	for w in workTime:

		if work.has_key(w.task.id):
			
			work[w.task.id]=work[w.task.id]+w.time
		else:
			work[w.task.id]=w.time
	total={}
	tasks = Task.objects.filter(worker = current_user);
	for t in tasks:
		if not work.has_key(t.id):
			work[t.id]=0
	for t in tasks:
		if work.has_key(t.id):
			total[t.id] = work[t.id]+t.duratino
	change=False
	workdays = {}
	currenttask = {}
	wtime_form = {}
	if int(request.GET.get('id', '0'))>0:
		change=True
		currenttask=Task.objects.get(id=request.GET.get('id', '0'))
		workdays = Work_Time.objects.filter(worker__id = current_user, task__id = request.GET.get('id', '0'))
		this_user=User.objects.get(id=current_user)
		wtime_form = Work_Time_Edit_Form(initial={'worker': current_user , 'task': currenttask })	
	if request.method == 'POST':
		wtime_form = Work_Time_Edit_Form(data=request.POST)		
		insprint = True
		inday = True
		taskid = request.POST.get('taskid')
		if wtime_form.is_valid():
			newdate = request.POST.get('day')
			taskid = request.POST.get('taskid')
			if taskid == '':
				taskid = request.POST.get('task')
			add = request.POST.get('addtype')
			newdate = datetime.datetime.strptime(newdate, '%m/%d/%Y')
			
			sprint = this_sprint
			start = sprint.start_date
			finish = sprint.finish_date
			start = datetime.datetime(start.year, start.month, start.day)	
			finish = datetime.datetime(finish.year, finish.month, finish.day)	
			t = date.today()
			today = datetime.datetime(t.year, t.month, t.day)
			
			if newdate > finish or newdate < start or newdate > today:
				error_sprint = '*Day must be active in sprint.'
				insprint= False
			if float(request.POST.get('time')) < 0:
				error_time = '*Number must be positive.'
				inday = False;
			if float(request.POST.get('time')) > 24:
				error_time = '*Number must be < 24.'
				inday = False;
			if insprint and inday:		
				
				workrecord = Work_Time.objects.filter(worker__id = current_user, task__id = taskid, day = newdate)
				
				if len(workrecord)>0:
					r=workrecord[0]
					if add == '1':
						if float(r.time)+float(request.POST.get('time')) > 24:
							error_time = '*Day work time exceeds 24 hours.'
							inday = False;
						else:
							r.time=float(r.time)+float(request.POST.get('time'))
					else:
						if float(r.time) - float(request.POST.get('time')) < 0:
							error_time = '*Day work time bellow 0.'
							inday = False;
						else:
							r.time=float(r.time)-float(request.POST.get('time'))
					r.save();
				else:
					if add == '1':
						newtime = wtime_form.save()
						newtime.save()
					else:
						newtime = wtime_form.save()
						t=0-float(request.POST.get('time'))
						newtime.time = t
						
						newtime.save()
				if (inday):	   
					change=False;
					update=True;
					workTime = Work_Time.objects.filter(worker__id = current_user)
					work={}
					for w in workTime:
						if work.has_key(w.task.id):
							
							work[w.task.id]=work[w.task.id]+w.time
						else:
							work[w.task.id]=w.time
					total={}
					tasks = Task.objects.filter(worker = current_user);
					for t in tasks:
						if not work.has_key(t.id):
							work[t.id]=0
					for t in tasks:
						if work.has_key(t.id):
							total[t.id] = work[t.id]+t.duratino
				else:
					change=True
					if taskid == '' :
						taskid=float(request.POST.get('task'))
					currenttask=Task.objects.get(id=taskid)
					workdays = Work_Time.objects.filter(worker__id = current_user, task__id = taskid)
					this_user=User.objects.get(id=current_user)
					wtime_form = Work_Time_Edit_Form(initial={'worker': current_user , 'task': currenttask })	
					
					#########################################
					# PG code here...						#
					#########################################
					
					#add previous all task in alltasks1
					alltasks1= allTasks
					
					
					# create 2d table allTasks
					allTsaks2 = [[0 for x in range(3)] for x in range(len(alltasks1))]
					
					for i in range (len(alltasks1)):
						# get remaining for each task
						remaining = Remaining.objects.filter (task = alltasks1[i])
						workdone = Work_Time.objects.filter (task = alltasks1[i]).aggregate(Sum('time'))
						print (workdone )
						allTsaks2[i][2] = remaining[len(remaining)-1].time + (0 if workdone['time__sum']==None else workdone['time__sum'])			
						allTsaks2[i][1] = remaining[len(remaining)-1].time
						allTsaks2[i][0] = alltasks1[i]
						
					#########################################
					#########################################
					
					
					return render_to_response('scrumko/mytask.html', {'error_sprint': error_sprint, 'inday':inday, 'insprint':insprint, 'error_time': error_time, 'update':update, 'wtime_form': wtime_form, 'workdays':workdays, 'currenttask': currenttask, 'change':change, 'total':total, 'work':work, 'workTime': workTime, 'allNotifications': allNotifications, 'note_permission': note_permission, 'allStories': allStories, 'allTasks': allTsaks2, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master}, context)	
			else: 
				change=True
				if taskid == '' :
					taskid=float(request.POST.get('task'))
				currenttask=Task.objects.get(id=taskid)
				workdays = Work_Time.objects.filter(worker__id = current_user, task__id = taskid)
				this_user=User.objects.get(id=current_user)
				wtime_form = Work_Time_Edit_Form(initial={'worker': current_user , 'task': currenttask })	
				
				#########################################
				# PG code here...						#
				#########################################
				
				#add previous all task in alltasks1
				alltasks1= allTasks
				
				
				# create 2d table allTasks
				allTsaks2 = [[0 for x in range(3)] for x in range(len(alltasks1))]
				
				for i in range (len(alltasks1)):
					# get remaining for each task
					remaining = Remaining.objects.filter (task = alltasks1[i])
					workdone = Work_Time.objects.filter (task = alltasks1[i]).aggregate(Sum('time'))
					print (workdone )
					allTsaks2[i][2] = remaining[len(remaining)-1].time + (0 if workdone['time__sum']==None else workdone['time__sum'])			
					allTsaks2[i][1] = remaining[len(remaining)-1].time
					allTsaks2[i][0] = alltasks1[i]
					
				#########################################
				#########################################
				
				return render_to_response('scrumko/mytask.html', {'error_sprint': error_sprint, 'inday':inday, 'insprint':insprint, 'error_time': error_time, 'update':update, 'wtime_form': wtime_form, 'workdays':workdays, 'currenttask': currenttask, 'change':change, 'total':total, 'work':work, 'workTime': workTime, 'allNotifications': allNotifications, 'note_permission': note_permission, 'allStories': allStories, 'allTasks': allTsaks2, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master}, context)	
		else:
			print wtime_form.errors
			change=True;
			return render_to_response('scrumko/mytask.html', {'error_sprint': error_sprint, 'inday':inday, 'insprint':insprint, 'error_time': error_time,'update':update, 'wtime_form': wtime_form, 'workdays':workdays, 'currenttask': currenttask, 'change':change, 'total':total, 'work':work, 'workTime': workTime, 'allNotifications': allNotifications, 'note_permission': note_permission, 'allStories': allStories, 'allTasks': allTsaks2, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master}, context)	
	
		
		
	return render_to_response('scrumko/mytask.html', {'notasks': notasks, 'error_sprint': error_sprint, 'inday':inday, 'insprint':insprint, 'error_time': error_time, 'update':update, 'wtime_form': wtime_form, 'workdays':workdays, 'currenttask': currenttask, 'change':change, 'total':total, 'work':work, 'workTime': workTime, 'allNotifications': allNotifications, 'note_permission': note_permission, 'allStories': allStories, 'allTasks': allTsaks2, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master}, context)

@login_required
def discussion(request):
	context = RequestContext(request)
	allPosts = Post.objects.filter(project__id=request.session['selected_project']).order_by('-id')
	allComments = Post_Comment.objects.filter()
	current_user = request.user.id
	selected_project_id = request.session['selected_project']
	
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	
	return render_to_response ('scrumko/discussion.html', {'allPosts': allPosts,'allComments': allComments, 'is_scrum_master' : is_scrum_master}, context)	
	

def add_new_post(request):
	project1=Project.objects.get(id = request.session['selected_project'])
	poster1=User.objects.get(id = request.user.id)
	Post.objects.create(project = project1, poster = poster1, content = request.POST['new_post'])
	return HttpResponseRedirect('/scrumko/discussion/')
	

def add_new_comment(request):
	post1=Post.objects.get(id = request.POST['postId'])
	commenter1=User.objects.get(id = request.user.id)
	Post_Comment.objects.create(post = post1, commenter = commenter1, comment = request.POST['new_comment'])
	return HttpResponseRedirect('/scrumko/discussion/')

def commentdelete(request, comment_id):
	context = RequestContext(request)
	comment_info = Post_Comment.objects.get(id=comment_id).delete()
	return HttpResponseRedirect("/scrumko/discussion")

def postdelete(request, post_id):
	context = RequestContext(request)
	post_info = Post.objects.get(id=post_id).delete()
	return HttpResponseRedirect("/scrumko/discussion")
	
@login_required
def documentation(request):
	context = RequestContext(request)
 	storyid=""
 	check=[];
 	selected_project_id = request.session['selected_project']
 	thisproject = Project.objects.get(id = selected_project_id)
 	all_stories = Story.objects.filter(project_name__id = selected_project_id)
 	all_notification = StoryNotification.objects.filter(story__project_name__id = selected_project_id)
 	documentation = Documentation.objects.filter(project__id = selected_project_id)
 	if len (documentation) <= 0:
 		docnew = Documentation.objects.create(project=thisproject, documentation_text="Documentation")
 		doc = docnew.documentation_text
 		documentation = Documentation.objects.filter(project__id = selected_project_id)
	
 	documentation[0].save();
 	doc = documentation[0].documentation_text
 	if request.method == 'POST':
		if request.POST.get('import', 0) != 0:
			documentation[0].documentation_text = request.POST['textarea']
			documentation[0].save();
			doc = documentation[0].documentation_text
			storyid = request.POST['story']
			story = Story.objects.get (id = storyid)
			check = request.POST.getlist('checks')
			newtext=''
			for m in check:
				if(m=='1'):
					newtext = newtext+ "<br><span style='font-weight:bold;font-size: 20px; color: #4590ab;'><br>"+story.story_name+"<br></span>"
				if(m=='2'):
					newtext = newtext+"<span style='font-weight:bold;'><br>"+story.text+"</span>"
				if(m=='3'):
					newtext = newtext+"<br>"+story.test_text
				if(m=='4'):
					note = StoryNotification.objects.filter(story__id = storyid)
					if len(note)>0:
						newtext = newtext+"<span style='color: orange;'><br>"+note[0].notification +"</span>"
					else:
						newtext = newtext+''
				
			doc = documentation[0].documentation_text + newtext
				#documentation[0].documentation_text = doc
				#documentation[0].save();
		else:
			documentation[0].documentation_text = request.POST['textarea']
			documentation[0].save();
			doc = documentation[0].documentation_text

 	return render_to_response ('scrumko/documentation.html', {'doc':doc, 'all_stories': all_stories, 'all_notification': all_notification}, context)

@login_required
def addstorytofinished(request, id):
	allcompleted=True
	noTask=True
	current_story = Story.objects.get(id = id)
	#story = Story.objects.get(id = id)
	current_user = request.user.id
	this_sprint=current_sprint(request)
	# if this_sprint!=None:
	allStories = Story_Sprint.objects.filter(sprint__id = current_sprint(request).id)
		# notasks=False;
	# else:
		# # ce ni taskov, te vrze na home
		# allStories = None;
		# notasks=True;
		# return render_to_response ('scrumko/notaskselected.html', {}, context)
	allTasks=Task.objects.filter(story__id = current_story.id);

	# stories = [];
	
	if allTasks == None:
		 return HttpResponseRedirect("/scrumko/home")

	for task in allTasks:
		print task.text 
		if task.story.id == current_story.id:
			if task.status == 0:
				#print 'accept task'  + task.text
				allcompleted=False
				noTask=False
			if  task.status == 1:	
				#print 'asigned'  + task.text
				allcompleted=False
				noTask=False
			if  task.status == 2:	
				print 'completed'  + task.text
				noTask=False
			if  task.status == 3:	
				#print 'pending' + task.text
				allcompleted=False
				noTask=False
					
				#prever ce se nima taskov
	print allcompleted	
		
	if allcompleted == True and noTask == False:
		current_story.status=True
		current_story.save()
	
	return HttpResponseRedirect("/scrumko/productbacklog")	
	
@login_required
def addstorytofinished2(request, id):
	context = RequestContext(request)
	current_story = Story.objects.get(id = id)
	print current_story.status
	current_story.status=True
	current_story.save()
	return HttpResponseRedirect("/scrumko/sprintbacklog")	
	
@login_required
def discardstory(request, id):
	context = RequestContext(request)
	current_story = Story.objects.get(id = id)
	current_story.estimation=0
	current_story.status=False
	current_story.save()
	return HttpResponseRedirect("/scrumko/productbacklog")

# function provides data for burndown
def get_burndown_data (request):
		
	# get project
	project_id = request.session.get('selected_project')
	
	# get start of first sprint
	fistsprint = Sprint.objects.filter (project_name__id = project_id)
	
	if len (fistsprint) == 0:
		return HttpResponse ([])
	
	start_date = fistsprint.aggregate (Min('start_date'))['start_date__min']
	
	# define array for returning data
	data = []
	
	# iterate thorught all dates to today
	
	d1 = start_date
	d2 = date.today()

	delta = d2 - d1

	for i in range(delta.days + 1):
		# date
		day = d1 + td(days=i)
		
		remaining = 0
		workload = 0
		
		#check all stories in project
		stories = Story.objects.filter (project_name__id = project_id);
		
		# go throught the stories
		for story in stories:
			#find tasks in this story
			tasks = Task.objects.filter (story = story)
			task_to_this_date = Remaining.objects.filter (task__story = story, day__lte = day)
			
			# check if task exsist
			# if not or not to this time then use story points
			# else use task remainings
			if len (tasks) == 0 or len (task_to_this_date) == 0:
				remaining += story.estimate * 6
				workload += story.estimate * 6
			else:
				# go throught all task and add
				for task in tasks:
					rems = Remaining.objects.filter (task = task, day__lte = day)
					worked = Work_Time.objects.filter (task = task, day__lte = day).aggregate(Sum('time'))
					print rems[len(rems) - 1].time
					remaining += 0 if len( rems ) == 0 else rems[len(rems) - 1].time
					
					workload += (0 if worked['time__sum'] == None else worked['time__sum']) + (0 if len( rems ) == 0 else rems[len(rems) - 1].time)
		
		data.append([i + 1, remaining, workload])
		
	return data
		
def get_progress_table (request):
	
	#array for data
	data = []
	
	# get all sprints
	sprints = Sprint.objects.filter (project_name__id = request.session.get('selected_project'))
	
	# numerate index
	index = 0
	
	# iterate throught sprint
	for sprint in sprints:
		index += 1
		# get planned velocity
		velocity = sprint.velocity
		
		# get story in sprint
		storysprint = Story_Sprint.objects.filter (sprint = sprint)
		
		# selected velocity
		selectedvelocity = 0
		realised = 0
		winput = 0
		
		# iterate throught storysprint
		for stsp in storysprint:
			selectedvelocity += stsp.story.estimate
			
			work = Work_Time.objects.filter (task__story = stsp.story).aggregate(Sum('time'))['time__sum']
			
			winput +=  0 if work == None else work
			
			if stsp.story.status == True:
				realised += stsp.story.estimate
		
		print (selectedvelocity)
		# calculate percentage
		percent = "%0.1f" % (0 if selectedvelocity == 0 else realised / selectedvelocity * 100) + ' %'
		
		# work input calc		
		data.append (['Sprint' + str(index), velocity, selectedvelocity, realised, percent, winput])
		
	return data
			
		
					
@login_required
def progress (request):
	context = RequestContext(request)
	cont_dict = {};
	
	# put data to dict
	data = get_burndown_data (request)
	cont_dict['data'] = json.dumps(data, cls=DecimalEncoder ) #cls=DecimalJSONEncoder
	
	cont_dict['tabledata'] = get_progress_table (request)	
	
	return render_to_response ('scrumko/progress.html', cont_dict, context)		
			
#class DecimalJSONEncoder(simplejson.JSONEncoder):
#	def default(self, o):
#		if isinstance(o, decimal.Decimal):
#			return str(o)
#		return super(DecimalJSONEncoder, self).default(o)	
	
		
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)	
		
		
	
	
	
	
