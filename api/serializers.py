from rest_framework import serializers
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from api.models import Player, Team, PlayerMembership, UserProfile


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    player = PlayerSerializer

    class Meta:
        model = UserProfile
        fields = ('id', 'player')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer
    player = serializers.SerializerMethodField('get_player_from_profile')

    class Meta:
        model = User
        fields = ('id', 'username', 'profile', 'player')

    def get_player_from_profile(self, profile):
        player = model_to_dict(profile.profile.player)
        return player


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMembership
        fields = ('id', 'player', 'team', 'date_joined')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'description')


class TeamFullSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'players')
