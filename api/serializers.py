from rest_framework import serializers
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from api.models import Player, Team, PlayerMembership, UserProfile


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ('id', 'name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position', 'photo')
        extra_kwargs = {'name': {'required': False}, 'surname': {'required': False}, 'height': {'required': False},
                        'year_of_birth': {'required': False}, 'position': {'required': False}}


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'player', 'user')


class UserSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField('get_player_from_profile')

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'player')
        extra_kwargs = {'password': {'write_only': True}}

    def get_player_from_profile(self, profile):
        player = PlayerSerializer(profile.profile.player)
        return player.data

    def create(self, validated_data):
        player = self.context['request'].data['player']
        user = User.objects.create_user(**validated_data)
        player = Player.objects.create(**player)
        UserProfile.objects.create(player=player, user=user)
        Token.objects.create(user=user)
        return user


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
