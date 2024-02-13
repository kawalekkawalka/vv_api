from datetime import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.models import Match, Team, UserFriendship, Player
from api.serializers.serializers import MatchSerializer, MatchFullSerializer, PlayerSerializer
from django.contrib.auth.models import User


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

        order = self.request.query_params.get('order')
        if order == 'desc':
            queryset = queryset.order_by('-id')

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

    @action(methods=['GET'], detail=False)
    def get_user_friends_matches(self, request):
        try:
            user = User.objects.get(id=self.request.query_params.get('user'))
            friendships = UserFriendship.objects.filter(
                Q(user1=user.id) | Q(user2=user.id)
            ).select_related('user1__profile__player', 'user2__profile__player')
            friends = {f.user1.profile.player_id: f.user1.profile.player for f in friendships} | \
                      {f.user2.profile.player_id: f.user2.profile.player for f in friendships}
            friends.pop(user.profile.player_id)

            now = datetime.now(timezone.utc)
            if self.request.query_params.get('time') == 'past':
                friends_matches = [
                    {
                        'match': MatchSerializer(Match.objects.filter(
                            Q(team1__players=friend) | Q(team2__players=friend),
                            time__lte=now,
                        ).order_by('-time').first()).data,
                        'player': PlayerSerializer(friend).data
                    } for friend in friends.values()
                ]
            else:
                friends_matches = [
                    {
                        'match': MatchSerializer(match).data,
                        'player': PlayerSerializer(friend).data
                    }
                    for friend in friends.values()
                    if (match := Match.objects.filter(
                        Q(team1__players=friend) | Q(team2__players=friend),
                        time__gte=now,
                    ).order_by('time').first())
                ]

            return Response(friends_matches, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'message': 'User has no friends'}, status=status.HTTP_200_OK)

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.team1.owner.id or request.user.id == instance.team2.owner.id:
            self.perform_destroy(instance)
        else:
            return Response({'message': 'You are not owner of the match'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)
