from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from scrumko.forms import UserForm, UserProfileForm, SprintCreateForm, ProjectCreateForm, StoryForm, ProjectEditForm, UserEditForm, NotificationPermissionForm, StoryEditForm
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from scrumko.models import User
from scrumko.models import UserProfile
from scrumko.models import Sprint, Project, Story, Poker, Poker_estimates, NotificationPermission


import json
#from scrumko.forms import UserForm, UserProfileForm

from decimal import Decimal

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
			request.session['selected_project'] = 0	
			request.session['project_name'] = ''
	
	# get information what roles user has on curent project
	selected_project_id = request.session['selected_project']
	is_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	
	# Construct a dictionary to pass to the template engine as its context.
	context_dict.update( {'is_owner':is_owner, 'is_scrum_master': is_scrum_master});	
				
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
                return HttpResponseRedirect('/scrumko/home/')
            else:
                # An inactive account was used - no logging in!
                success=False;
                return HttpResponse("Your Rango account is disabled.")
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


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/scrumko/')

@login_required
def productbacklog(request):
	#allStories = Story.objects.all()
	allStories = Story.objects.filter(project_name__id=request.session['selected_project'])
	
	current_user = request.user.id
	selected_project_id = request.session['selected_project']
	is_owner = len (Project.objects.filter(project_owner__id = current_user, id = selected_project_id)) > 0
	is_scrum_master = len (Project.objects.filter(scrum_master__id = current_user, id = selected_project_id)) > 0
	
	context = RequestContext(request)
	return render_to_response('scrumko/productbacklog.html', {'allStories': allStories, 'is_owner': is_owner, 'is_scrum_master': is_scrum_master}, context)
	
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
@user_passes_test(lambda u: u.is_superuser)
#@transaction.atomic

def maintainsprint(request):
	context = RequestContext(request)
	sprint_info = Sprint.objects.filter(project_name__id=request.session['selected_project'])
	sprint_data = {"sprint_detail" : sprint_info}
    # Render the template depending on the context.
	return render_to_response('scrumko/sprintcreate.html',sprint_data, context)
	
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
			notification_permission.permission=request.POST.get('is_private', False)
			notification_permission.save()
		
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
	
def maintainsprint(request):
	context = RequestContext(request)
	sprint_info = Sprint.objects.filter(project_name__id=request.session['selected_project'])
	sprint_data = {"sprint_detail" : sprint_info}
    # Render the template depending on the context.
	return render_to_response('scrumko/maintainsprint.html',sprint_data, context)
	
def sprintedit(request):
	context = RequestContext(request)
	sprint_form = Sprint.objects.all()
	sprint_data = {"sprint_form" : sprint_form}
    # Render the template depending on the context.
	return render_to_response('scrumko/sprintedit.html',sprint_data, context)


def sprintdelete(request, sprint_id):
	context = RequestContext(request)
	sprint_info = Sprint.objects.get(id=sprint_id).delete()
	return HttpResponseRedirect("/scrumko/maintainsprint")	

def maintainproject(request):
	context = RequestContext(request)
	project_info = Project.objects.all()
	project_data = {"project_detail" : project_info}	
    # Render the template depending on the context.
	return render_to_response('scrumko/maintainproject.html', project_data, context)
	
def projectdelete(request, id):
	context = RequestContext(request)
	projecr_info = Project.objects.get(id=id).delete()
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
					return render_to_response('scrumko/editproject.html',{'notification_form': notification_form, 'already_exist_message': already_exist_message, 'project_form': project_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options, "project_detail" : project_info}, context)
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
				
				notification_permission = notification_form.save(commit=False)
				notification_permission.project = project_info[0]
				notification_permission.permission=request.POST.get('is_private', False)
				notification_permission.save()

				registered = True	
				all_members=""

		else:
			print project_form.errors
			return render_to_response('scrumko/editproject.html',{'notification_form': notification_form, 'already_exist_message': already_exist_message, 'project_form': project_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options, "project_detail" : project_info}, context)

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
		

	print r.id
	notif_perm=NotificationPermission.objects.filter(project__id=r.id)
	project_form = ProjectEditForm(initial={'project_name': r.project_name, 'project_owner': r.project_owner, 'scrum_master': r.scrum_master, 'team': r.team})
	notification_form = NotificationPermissionForm(initial={'permission': notif_perm[0].permission})
	# Render the template depending on the context.
	return render_to_response('scrumko/editproject.html',{'notification_form': notification_form, 'already_exist_message': already_exist_message, 'project_form': project_form, 'registered': registered, 'all_members': all_members, 'all_options': all_options, "project_detail" : project_info}, context)
	

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
			return render_to_response('scrumko/edit.html',{ 'user_form': user_form, 'registered': registered, "project_detail" : project_info}, context)
	
	else:
		userid = int(request.GET.get('id', '0'))
		project_info = User.objects.filter(id = userid)
		r = project_info[0]	
	user_form = UserEditForm(initial={'username': r.username, 'email': r.email, 'is_superuser': r.is_superuser, 'first_name': r.first_name, 'last_name': r.last_name, 'password': r.password, 'password2': r.password })
	
	return render_to_response('scrumko/edit.html',{ 'user_form': user_form, 'registered': registered, 'project_detail' : project_info}, context)

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
	# get context
	context = RequestContext(request)
	
	# initialize dictionary to push content on page
	context_dict = {}
	
	# get active stoy on planing poker
	active_poker = Poker.objects.filter (project__id = request.session['selected_project'])
	active_poker = active_poker[len(active_poker) - 1]	
	
	## add data to dictionary
	
	# if not active poker, then writeout this
	if not active_poker:
		context_dict.update ({'story_text' : 'There is not active planing pokers right now.'})
	
	#if data available write-out
	else:
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
			estimate_value[i][j+2] = avg / num
			
		# check if last planing poker has no my submision
		my_last = Poker_estimates.objects.filter (poker = pokers[i], user__id = current_user)
		last_estimate = len (my_last ) == 0
		
	return {'estimate_value' : estimate_value, 'users_value' : users_value, 'last_round' : last_estimate	}

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
		button_dict.update ({'activeround' : True })
	else:
		button_dict.update ({'activeround' : False })

	## estimated from this user?
	
	# get estimates of this user for current active story
	estimates = Poker_estimates.objects.filter (poker__project__id = project_id, poker__active = True, user__id = current_user)
	
	# check if exsist
	
	if len (estimates) > 0 or len (active_poker) == 0:
		button_dict.update ({'estimates' : False })
	else:
		button_dict.update ({'estimates' : True })
	
	print button_dict['scrummaster']
	
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
	
	print estimate
		
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
	for e in est:
		total = total + e.estimate
	
	return total
	
	
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
	
