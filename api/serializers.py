from rest_framework import serializers

from api.models import Player, Team, PlayerMembership


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


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
