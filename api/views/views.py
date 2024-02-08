from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from api.models import Player, Team, UserProfile, PlayerMembership, Comment, Match, TeamInvitation, PlayerRecords
from api.serializers.player_records_serializers import PlayerRecordsSerializer
from api.serializers.serializers import PlayerSerializer, TeamSerializer, TeamFullSerializer, UserSerializer, UserProfileSerializer, \
    ChangePasswordSerializer, MemberSerializer, CommentSerializer, MatchSerializer, TeamInvitationSerializer, \
    MatchFullSerializer, PlayerFullSerializer, TeamPlayerSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=['PUT'], detail=True, serializer_class=ChangePasswordSerializer,
            permission_classes=(IsAuthenticated,))
    def change_pass(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'message': 'Wrong old password'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'Password updated'}, status=status.HTTP_200_OK)


class UserProfileViewset(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class PlayerViewset(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PlayerFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)


class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Comment.objects.all()

        player_id = self.request.query_params.get('player')
        if player_id is not None:
            queryset = queryset.filter(player=player_id)

        team_id = self.request.query_params.get('team')
        if team_id is not None:
            queryset = queryset.filter(team=team_id)

        match_id = self.request.query_params.get('match')
        if match_id is not None:
            queryset = queryset.filter(match=match_id)

        match_performances_amount = int(self.request.query_params.get('amount', default=100))
        queryset = queryset[:match_performances_amount]
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        content_type_name = data.get('content_type')
        content_type = ContentType.objects.get(model=content_type_name)
        user = User.objects.get(pk=data.get('user'))
        comment = Comment.objects.create(content_type=content_type, user=user, object_id=data.get('object_id'),
                                         description=data.get('description'))
        result = CommentSerializer(comment, many=False)
        return Response({'message': 'Comment added', 'result': result.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        response = {'message': 'Method not allowed'}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['DELETE'], detail=False, permission_classes=(IsAuthenticated,))
    def delete_comment(self, request):
        if request.data:
            comment_id = request.data
            try:
                comment = Comment.objects.get(pk=comment_id)
                if comment.user == request.user:
                    comment.delete()
                    response = {'message': 'Successfully deleted'}
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {'message': 'Its not your comment'}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            except:
                response = {'message': 'Wrong comment id'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)


class MemberViewset(viewsets.ModelViewSet):
    queryset = PlayerMembership.objects.all()
    serializer_class = MemberSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['POST'], detail=False)
    def join(self, request):
        if 'player' in request.data and 'team' in request.data:
            player = Player.objects.get(id=request.data['player'])
            team = Team.objects.get(id=request.data['team'])

            if PlayerMembership.objects.filter(player=player, team=team).exists():
                member = PlayerMembership.objects.get(player=player, team=team)
                member.date_left = None
                member.save()
                response = {'message': 'Rejoined team'}
                return Response(response, status=status.HTTP_200_OK)

            member = PlayerMembership.objects.create(player=player, team=team)
            serializer = MemberSerializer(member, many=False)
            response = {'message': 'Added to team', 'results': serializer.data}
            return Response(response, status=status.HTTP_201_CREATED)

        else:
            response = {'message': 'Wrong parameters'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def leave(self, request):
        if 'player' in request.data and 'team' in request.data:
            player = Player.objects.get(id=request.data['player'])
            team = Team.objects.get(id=request.data['team'])
            member = PlayerMembership.objects.get(player=player, team=team)
            member.date_left = date.today()
            member.save()
            response = {'message': 'Removed from team'}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'message': 'Wrong parameters'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


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
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = Team.objects.all()
        player_id = self.request.query_params.get('player')
        if player_id is not None:
            player = get_object_or_404(Player, id=player_id)
            queryset = queryset.filter(players__id=player.id)
            serializer = TeamPlayerSerializer(queryset, many=True, context={'player_id': player_id})
        else:
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
            return Response('You are not owner of the team', status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        user_serializer = UserSerializer(user, many=False)
        return Response({'token': token.key, 'user': user_serializer.data})


class TeamInvitationViewset(viewsets.ModelViewSet):
    queryset = TeamInvitation.objects.all()
    serializer_class = TeamInvitationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        if 'user' in request.data and 'team' in request.data:
            user = User.objects.get(id=request.data['user'])
            team = Team.objects.get(id=request.data['team'])

            if TeamInvitation.objects.filter(user=user, team=team).exists():
                response = {'message': 'Invitation already sent before'}
                return Response(response, status=status.HTTP_200_OK)

            invitation = TeamInvitation.objects.create(user=user, team=team)
            serializer = TeamInvitationSerializer(invitation, many=False)
            response = {'message': 'Invitation sent', 'results': serializer.data}
            return Response(response, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = TeamInvitation.objects.all()

        team_id = self.request.query_params.get('team')
        if team_id is not None:
            queryset = queryset.filter(team=team_id)

        return queryset

    def destroy(self, request, *args, **kwargs):
        response = {'message': 'Method not allowed'}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['DELETE'], detail=False, permission_classes=(IsAuthenticated,))
    def delete_invitation(self, request):
        if request.data:
            invitation_id = request.data
            try:
                invitation = TeamInvitation.objects.get(pk=invitation_id)
                invitation.delete()
                response = {'message': 'Successfully deleted'}
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {'message': 'Wrong invitation id'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)


class PlayerRecordsViewset(viewsets.ModelViewSet):
    queryset = PlayerRecords.objects.all()
    serializer_class = PlayerRecordsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        player_id = self.request.query_params.get('player')
        if player_id is not None:
            return PlayerRecords.objects.filter(player=player_id)
        return PlayerRecords.objects.all()
