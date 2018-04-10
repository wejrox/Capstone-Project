from django.contrib.auth.models import User, Group
from apps.api.models import Profile, Availability, Session
from rest_framework import viewsets
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import requests
import json
from mysite.forms import FeedbackForm, DeactivateUser, RegistrationForm, EditProfileForm, ConnectAccountForm, UserAvailabilityForm, EditAvailabilityForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import login as contrib_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

# Import settings
from django.conf import settings

# Method to get data from INTERNAL API (Meshwell API)
# Takes a table name, and parameters in the form of 'username=root' or similar
def retrieve_data(table, *params):
	url = 'http://127.0.0.1/api/'+table+'/?format=json'
	# Add the additional parameters
	for string in params:
		url += '&'+string

	headers = { 'Authorization':'Token ' + settings.API_TOKEN }
	response = requests.get(url, headers=headers)
	if response.ok:
		data = response.json()
		return data
	return None

# Deletes data from the database using the INTERNAL API (Meshwell API)
# Takes an API url address to delete
def delete_data(url):
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }
	response = requests.delete(url, headers=headers)

	if response.ok:
		print('deleted the entry')
		return True
	else:
		print('couldn\'t unlink the entry')
		print(response.status_code)
		return False

# Index page/Landing page
def index(request):
	data = retrieve_data('game')

	context = {'games':{}}
	if data:
		for game in data:
			g = { 'name':game['name'], 'description':game['description'] }
			context['games'][game['name']] = g

	# Give back the context to the index page
	return render(request, 'mysite/index.html', context)

# User dashboard
@login_required
def dashboard(request):
	context = {
		'title':'Dashboard',
		'message':'This is a stub page for the dashboard. No functionality has been added yet.',
	}

	data = retrieve_data('profile', 'id=2')
	print(data)
	return render(request, 'mysite/dashboard.html', context)

#views for the profile page
@login_required
def profile(request):
	#reference from index function
	if request.user.is_authenticated:
		headers = { 'Authorization':'Token ' + settings.API_TOKEN }
		profile = Profile.objects.filter(user=request.user.id).first()
		if not profile:
			profile = Profile.objects.create(user=request.user)
		url = 'http://127.0.0.1/api/profile/' + str(profile.id) + '/?format=json'
		response = requests.get(url, headers=headers)
		data = response.json()

		#Dummy Data
		context = {
			'username':data['user']['username'],
			'first_name':data['user']['first_name'],
			'last_name':data['user']['last_name'],
			'pref_server':data['pref_server'],
			'birth_date':data['birth_date'],
			'sessions_played':data['sessions_played'],
			'teamwork_commends':data['teamwork_commends'],
			'positivity_commends':data['positivity_commends'],
			'skill_commends':data['skill_commends'],
			'communication_commends':data['communication_commends'],
		}
		return render(request, 'mysite/profile.html', context)
	else:
		context = {'error_title':'Not logged in', 'message':'You must be logged in to view this page'}
		return render(request, 'mysite/error_page.html', context)

# CSS Standarisation Page
def css_standard(request):
	context = {
		'title':'CSS Standard',
	}
	return render(request, 'mysite/css_standard.html', context)

# Catalog of games
def catalog(request):
	context = {
		'title':'Games Catalog',
		'message':'This is a stub page for our games catalog. No functionality has been added yet.',
	}
	return render(request, 'mysite/catalog.html', context)

# About us
def about_us(request):
	context = {
		'title':'About Us',
		'message':'This is a stub page for the about us page. No functionality has been added yet.',
	}
	return render(request, 'mysite/about_us.html', context)

#views for the feedback form page
def feedback(request):
	title = 'Feedback'
	form = FeedbackForm(request.POST)
	context = {
		'title': title,
		'form': form,
		'message': 'Please enter your details and feedback below. Your feedack is greatly appreciated, and helps us to provide a better service!',
		'success': 'False',
	}
	if request.method == 'POST':
		if form.is_valid():
			#saving details from the feedback form
			instance = form.save(commit=False)
			instance.save()

			context = {
				'title': 'Feedback submittted',
				'message': 'Thank you for your feedback!',
				'success': 'True',
			}
			return render(request, 'mysite/feedback.html', context)
	else:
		return render(request, 'mysite/feedback.html', context)

#views for the registration page
def register(request):
	# Ensure there is nobody logged in
	if request.user.is_authenticated:
		return redirect('dashboard')

	title = 'Register'
	form = RegistrationForm(request.POST)

	if request.method =='POST':
		# Create the user
		if form.is_valid():
			user = form.save()
			user.refresh_from_db() #load profile created by register
			user.save()
			user.refresh_from_db()
			# Get username and password to log in with
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			# Set the profile birth_date to the one given
			profile = Profile.objects.get(user=user)
			profile.birth_date = form.cleaned_data.get('birth_date')
			profile.save()

			# Redirect to login page
			return redirect('login')
	else:
		# Recreate the form since we aren't posting
		form = RegistrationForm()
		# Send the form to the page and render it
		return render(request, 'registration/register.html', {'form':form})

	# Return the form if the form isn't valid but post was specified
	return render(request, 'registration/register.html', {'form':form})

#Views for Edit Profile page
@login_required
def edit_profile(request):
	if request.method == 'POST':
		form = EditProfileForm(request.POST, instance=request.user)
		context = {
			'form':form,
		}

		if form.is_valid():
			form.save()
			#return HttpResponseRedirect(reverse('registration/login.html'))
			return redirect('login')
		else:
			form = EditProfileForm(instance=request.user)
			return render(request, 'mysite/edit_profile.html', context)
	else:
		form = EditProfileForm(instance=request.user)
		context = { 'form':form, }
		return render(request, 'mysite/edit_profile.html', context)

# Login. Implemented here to prevent logged in users from accessing the page
def login(request):
	if request.user.is_authenticated:
		return redirect(settings.LOGIN_REDIRECT_URL)
	return contrib_login(request)

# Logging out. Currently loads a page. Recommend logging out to open a popup box that the user must click 'OK' to and be redirected to index.
@login_required
def logout(request):
	logout(request)

@login_required
def deactivate_user(request):
	form = DeactivateUser()
	context = {
		'title': 'Confirm Details',
		'message': 'Please enter your login details in order to confirm deactivation.',
		'success': 'False',
		'form': form,
	}
	if request.method == 'POST':
		form = DeactivateUser(request.POST)
		#using built-in Authentication Form
		#username = request.POST['username']
		#password = request.POST['password']

		if form.is_valid():
			# Authenticate the user details they entered
			user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
			# User details entered must be the user that is logged in
			if request.user == user:
				user.is_active = False
				user.save()

				context = {
					'title': 'Account Deactivated',
					'message': 'Your account has been deactivated',
					'success': 'True',
				}
				return render(request, 'registration/deactivate_success.html', context)
			else:
				return redirect('index')
	# Show the deactivate page again if the form is invalid or if no form was posted
	return render(request, 'registration/deactivate.html', context)

@login_required
def connect_account(request):
	form = ConnectAccountForm()
	context = {
		'title':'Connect Game Account',
		'form':form,
	}

	if request.method == 'POST':
		form = ConnectAccountForm(request.POST)
		if form.is_valid():
			ranks = None
			# Get the rank depending on which game was selected
			if form.cleaned_data['game'].name == 'Rainbow Six Siege':
				# Ensure profile's game doesn't already have an account connected to it
				connected_account = retrieve_data('profile_connected_game_account', 'profile='+str(request.user.profile.id))
				if not connected_account:
					ranks = get_r6siege_ranks(request, form.cleaned_data['game_player_tag'])
				else:
					context['error'] = 'You already have an account connected for this game.'
					return render(request, 'registration/connect_account.html', context)

			# Create a new instance so long as we found some ranks
			if ranks is not None:
				# Create a new instance from the form
				instance = form.save(commit=False)
				instance.profile = request.user.profile
				instance.cas_rank = ranks['cas_rank']
				instance.comp_rank = ranks['comp_rank']
				instance.save()

				return redirect('connected_accounts')
			else:
				context['error'] = 'The account name you have entered does not exist'
				return render(request, 'registration/connect_account.html', context)
		else:
			return render(request, 'registration/connect_account.html', context)

	else:
		return render(request, 'registration/connect_account.html', context)

	return render(request, 'registration/connect_account.html', context)

@login_required
def connected_accounts(request):
	connected_accounts = retrieve_data('profile_connected_game_account', 'profile='+str(request.user.profile.id))
	games = retrieve_data('game')
	# Headers needed since we have to get the game name still
	headers = { 'Authorization':'Token ' + settings.API_TOKEN }

	# Pre-create the games that we have
	final_data = {}
	for game in games:
		final_data[game['url']] = {}
		final_data[game['url']]['game_name'] = game['name']
		final_data[game['url']]['game_player_tag'] = 'Not Connected!'

	# Set each account to be inside the game if it exists
	if connected_accounts and games:
		# Assign each of the accounts by accessing related to game url
		for account in connected_accounts:
			final_data[account['game']]['game_player_tag'] = account['game_player_tag']
			final_data[account['game']]['platform'] = account['platform']
			final_data[account['game']]['cas_rank'] = account['cas_rank']
			final_data[account['game']]['comp_rank'] = account['comp_rank']
			final_data[account['game']]['connected'] = True


	context = { 'title':'Connected Accounts', 'accounts':final_data, }

	# User clicks unlink button
	if(request.GET.get('Unlink Account')):
		unlink_account(request.user.profile, request.GET.get('game'))
		return redirect('connected_accounts')

	return render(request, 'mysite/connected_accounts.html', context)

# Remove the record of the connected account
@login_required
def unlink_account(profile, game_name):
	record = retrieve_data('profile_connected_game_account', 'profile='+str(profile.id), 'game='+game_name)
	if record:
		delete_data(record[0]['url'])

# Gets the player details specified, or None if there are multiple entries
# Decides on region based on the profiles region. (Perhaps change later?)
@login_required
def get_r6siege_ranks(request, player_tag):
	url = 'https://r6db.com/api/v2/players?name=' + player_tag
	headers = { 'X-App-Id':'MyRequest' }
	response = requests.get(url, headers=headers)
	data = response.json()
	print(player_tag)
	# Cancel the check if the user was not found or too many were found
	if not response.ok or len(data) > 1:
		return None

	# Decide which region to check
	region = request.user.profile.pref_server
	if region == 'oce' or region == 'as' or region == 'me':
		region = 'apac'
	elif region == 'saf' or region == 'usw' or region == 'use':
		region = 'ncsa'
	elif region == 'eu' or region == 'saf':
		region = 'emea'

	ranks = { 'cas_rank':0, 'comp_rank':0 }

	ranks['cas_rank'] = 0
	ranks['comp_rank'] = data[0]['ranks'][region]['mmr']

	return ranks

@login_required
def user_preference(request):
	form = UserPreferenceForm()
	context = {
		'title': 'User Preference',
		'message': 'Please enter your preference details.',
		'success': 'False',
		'form': form,
	}
	if request.user.is_authenticated:
		if request.method == 'POST':
			form = UserPreferenceForm(request.POST)

			if form.is_valid():
				form.save()
				context = {
					'title': 'Preference created.',
					'message': 'Your preference is created.',
					'success': 'True',
				}
				return render(request, 'registration/preference_success.html', context)
			else:
				form = UserPreferenceForm()
				return render(request, 'registration/preference.html', context)
		else:
			form = UserPreferenceForm()
			return render(request, 'registration/preference.html', context)
	else:
		context = {'error_title':'Not logged in', 'message':'You must be logged in to view this page'}
		return render(request, 'mysite/error_page.html', context)

@login_required
def enter_queue(request):
# get the user from the Django request & map to variable
	django_user = request.user
  #link user_profile to django users profile model & get user's profile
	user_profile = django_user.profile
	#user_profile = Profile.objects.get(user=request.user)
  #Map user_availabilities variable to profile from Availability model
	users_availabilities = Availability.objects.filter(profile=user_profile) #mapping user_avail to user profile
	if users_availabilities is not None:
		return HttpResponse("Failed to Join Queue,Set Availability & Try again")
		return HttpResponseRedirect('//profile')
	else:
		#creating an array to store all matching sessions
		all_matching_sessions = []
		# avail is each Availability object

		for avail in users_availabilities:
			#if avail.end_time is None:
			#return HttpResponse("FAILED")
			#return HttpResponseRedirect('account/profile/')
			#else:
			matching_sessions = Session.objects.filter(end_time__lte=avail.end_time)#looping through all the sessions end times that match to availability
    		#adding them to the array
			all_matching_sessions = all_matching_sessions + matching_sessions

			#If no matching sessions are available
			if len(all_matching_sessions) == 0:
				#create a session
				player_session = Session(
					#game = 'random_game',
					start_time = users_availabilities[0].start_time,
					end_time = users_availabilities[0].end_time,
				)
				player_session.save()
				return render(request, 'mysite/profile.html')

			else:
				player_session = Session(
					session = all_matching_sessions[0],
					profile = user_profile
				)
				player_session.save()
				#return HttpResponse('Waiting in queue')
				return render(request, 'mysite/profile.html')

@login_required
def exit_queue(request):
    player_session.delete()

@login_required
def availability(request):
	avail = retrieve_data('availability', 'profile='+str(request.user.profile.id))
	print(avail)
	context = {'title':'Availability', 'Message':'Below is a list of your current availabilities', 'availabilities':avail}

	# Delete data based on the the id provided by the html page
	if(request.GET.get('Remove Availability')):
		delete_data(request.GET.get('url'))
		return redirect('availability')

	# Redirect to an edit availability page, given the id of the profile to edit
	if(request.GET.get('Edit Availability')):
		print("Edit availability Clicked")
		# Show edit form? idk

	return render(request, 'mysite/availability.html', context)

@login_required
def add_availability(request):
	form = UserAvailabilityForm()
	context = {
		'title': 'User Availability',
		'message': 'Please enter your Availability details.',
		'success': 'False',
		'form': form,
	}

	if request.method == 'POST':
		form = UserAvailabilityForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.profile = request.user.profile
			instance.save()
			context = {
				'title': 'Availability created.',
				'message': 'Your Availability is created.',
				'success': 'True',
			}
			return redirect('availability')
		else:
			return render(request, 'registration/add_availability.html', context)
	else:
		form = UserAvailabilityForm()
		return render(request, 'registration/add_availability.html', context)

@login_required
def edit_availability(request):
        form = EditAvailabilityForm()
        context = {
                'title': 'Update Availabilities',
                'message' : 'Please enter your new Availabilities.',
                'success' : 'False',
        }

        if request.method == 'POST':
                form = EditAvailability(request.POST, instance=request.user)
                if form.is_valid():
                        form.save()
                        context = {
                                'title' : 'Successfully updated Availabilites.',
                                'message' : 'Your Availabilites have been updated',
                                'success' : 'True',
                        }
                        return redirect('availability')
                else:
                        form = EditAvailabilityForm()
                        return render(request, 'registration/edit_availability.html', context)
        else:
                form = EditAvailabilityForm()
                return render(request, 'registration/edit_availability.html',   context)
