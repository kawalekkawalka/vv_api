from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.models import Match, Team
from api.serializers.serializers import MatchSerializer, MatchFullSerializer, PlayerSerializer


class MatchViewset(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = Match.objects.get(pk=kwargs['pk'])
        serializer = MatchFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Match.objects.all().order_by('-time')

        team_id = self.request.query_params.get('team')
        if team_id is not None:
            queryset = queryset.filter(Q(team1=team_id) | Q(team2=team_id))

        player_id = self.request.query_params.get('player')
        if player_id is not None:
            team_ids = Team.objects.filter(players__id=player_id).values_list('id', flat=True)
            queryset = queryset.filter(Q(team1__in=team_ids) | Q(team2__in=team_ids))

        time = self.request.query_params.get('time')
        if time is not None:
            actual_time = timezone.now()
            if time == "past":
                queryset = queryset.filter(time__lte=actual_time)
            if time == "future":
                queryset = queryset.filter(time__gte=actual_time).order_by('time')

        match_amount = int(self.request.query_params.get('amount', 0))
        if match_amount:
            queryset = queryset[:match_amount]
        return queryset

    @action(methods=['GET'], detail=False)
    def get_match_participants(self, request):
        match_id = self.request.query_params.get('match')
        if match_id is not None:
            match = Match.objects.get(id=match_id)
            players = set()
            for team in (match.team1, match.team2):
                players.update(team.players.all())
            return Response(PlayerSerializer(players, many=True).data, status=status.HTTP_200_OK)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            team1 = Team.objects.get(name=request.data['team1'])
            team2 = Team.objects.get(name=request.data['team2'])
            if team1 != team2:
                match = Match.objects.create(team1=team1, team2=team2, time=request.data['time'])
            else:
                return Response({'message': 'Provided same team two times'}, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist:
            return Response({'message': 'One or both teams do not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(MatchSerializer(match).data, status=status.HTTP_201_CREATED)
