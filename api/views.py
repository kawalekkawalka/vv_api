from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from api.models import Player, Team
from api.serializers import PlayerSerializer, TeamSerializer, TeamFullSerializer


class PlayerViewset(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class TeamViewset(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TeamFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)

