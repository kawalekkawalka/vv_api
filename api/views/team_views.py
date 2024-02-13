from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models import Team, Player, UserProfile, PlayerMembership
from api.serializers.serializers import TeamSerializer, TeamPlayerSerializer, TeamFullSerializer


class TeamViewset(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Team.objects.all()
        player_id = self.request.query_params.get('player')
        if player_id is not None:
            player = get_object_or_404(Player, id=player_id)
            queryset = queryset.filter(players__id=player.id)
        team_amount = int(self.request.query_params.get('amount', 0))
        if team_amount:
            queryset = queryset[:team_amount]
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = Team.objects.all()
        player_id = self.request.query_params.get('player')
        team_amount = int(self.request.query_params.get('amount', 0))
        if player_id is not None:
            player = get_object_or_404(Player, id=player_id)
            queryset = queryset.filter(players__id=player.id)
            if team_amount:
                queryset = queryset[:team_amount]
            serializer = TeamPlayerSerializer(queryset, many=True, context={'player_id': player_id})
        else:
            order = self.request.query_params.get('order')
            if order == 'desc':
                queryset = queryset.order_by('-id')
            team_amount = int(self.request.query_params.get('amount', 0))
            if team_amount:
                queryset = queryset[:team_amount]
            serializer = TeamSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TeamFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        player = UserProfile.objects.get(user_id=request.user.id).player
        PlayerMembership.objects.create(player=player, team=team)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.owner.id:
            self.perform_destroy(instance)
        else:
            return Response({'message': 'You are not owner of the team'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_teams_names(self, request):
        owner_id = self.request.query_params.get('owner')
        if owner_id:
            teams = Team.objects.filter(owner=owner_id).values_list('name', flat=True)
        else:
            teams = Team.objects.all().values_list('name', flat=True)
        return Response(teams, status=status.HTTP_200_OK)
