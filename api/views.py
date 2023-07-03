from django.shortcuts import render
from rest_framework import viewsets

from api.models import Player, Team
from api.serializers import PlayerSerializer, TeamSerializer


class PlayerViewset(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class TeamViewset(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
