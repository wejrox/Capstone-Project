from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth import validators
from django.forms import ValidationError
from django.db import IntegrityError
from django.utils.translation import gettext as _
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Feedback, Banned_User
from django.contrib.auth.hashers import check_password, make_password


class UserSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Users.
	'''
	class Meta:
		model = User
		fields = ('username', 'password', 'date_joined', 'last_login', 'first_name', 'last_name', 'email', 'groups', 'is_staff', 'is_active', 'is_superuser')
		extra_kwargs = {
            		'username': {'validators': [validators.UnicodeUsernameValidator]},
        	}


	def validate(self, data):
		'''
		Throws a ValidationError if the user provided (if valled via post) already exists.
		'''
		if self.context['request']._request.method == 'POST':
			if User.objects.filter(username=data['username']):
				raise serializers.ValidationError('Username already exists')
		return data


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Profiles.
	'''
	user = UserSerializer(required='True')

	class Meta:
		model = Profile
		fields = '__all__'

	
	def create(self, validated_data):
		'''
		Create a new User and Profile.
		'''
		# Create User object.
		user_data = validated_data.pop('user')
		user = User.objects.create()

		# Groups must be set this way due to being unable to set many-many relationships.
		group_name = user_data.get('groups', user.groups)
		if group_name:
			user_group = Group.objects.get(name=group_name[0])
			user_group.user_set.add(user)

		# Create password hash.
		user.password = make_password(user_data.get('password', user.password))

		# Set standard user details.
		user.username = user_data.get('username', user.username)
		user.date_joined = user_data.get('date_joined', user.date_joined)
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)

		# Generate profile and save.
		profile = Profile.objects.create(user=user, **validated_data)
		user.save()

		# Return the profile's details after creation.
		return profile

	
	def update(self, instance, validated_data):
		'''
		Update the User and Profile to the data provided.
		'''

		# Get user information.
		user_data = validated_data.pop('user')
		user = instance.user

		# Update profile.
		instance.pref_server = validated_data.get('pref_server', instance.pref_server)
		instance.birth_date = validated_data.get('birth_date', instance.birth_date)
		instance.sessions_played = validated_data.get('sessions_played', instance.sessions_played)
		instance.teamwork_commends = validated_data.get('teamwork_commends', instance.teamwork_commends)
		instance.sportsmanship_commends = validated_data.get('sportsmanship_commends', instance.sportsmanship_commends)
		instance.skill_commends = validated_data.get('skill_commends', instance.skill_commends)
		instance.communication_commends = validated_data.get('communication_comments', instance.communication_commends)

		# Update user.
		user.username = user_data.get('username', user.username)

		# Only set new password if password changed.
		if not check_password(user_data.get('password'), user.password):
			user.password = make_password(user_data.get('password', user.password))
		user.email = user_data.get('email', user.email)
		user.first_name = user_data.get('first_name', user.first_name)
		user.last_name = user_data.get('last_name', user.last_name)

		# Update groups if any have been selected.
		group_name = user_data.get('groups', user.groups)
		if group_name:
			user_group = Group.objects.get(name=group_name[0])
			user_group.user_set.add(user)

		# Save to the database.
		instance.save()
		user.save()

		return instance


class AvailabilitySerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Availabilities.
	'''
	class Meta:
		model = Availability
		fields = '__all__'


class GameSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Games.
	'''
	class Meta:
		model = Game
		fields = '__all__'


class Game_RoleSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Game Roles.
	'''
	class Meta:
		model = Game_Role
		fields = '__all__'


class SessionSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Sessions.
	'''
	class Meta:
		model = Session
		fields = '__all__'


class Session_ProfileSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Session Profiles.
	'''
	class Meta:
		model = Session_Profile
		fields = '__all__'


class ReportSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Reports.
	'''
	class Meta:
		model = Report
		fields = '__all__'


class Profile_Connected_Game_AccountSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Profile Connected Game Accounts.
	'''
	class Meta:
		model = Profile_Connected_Game_Account
		fields = '__all__'


class FeedbackSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Feedback submissions.
	'''
	class Meta:
		model = Feedback
		fields = '__all__'


class Banned_UserSerializer(serializers.HyperlinkedModelSerializer):
	'''
	Handles serialisation of Banned Users.
	'''
	class Meta:
		model = Banned_User
		fields = '__all__'
