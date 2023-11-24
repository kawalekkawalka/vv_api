from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from api.models import Player, Team, UserProfile, PlayerMembership, Comment, Match, TeamInvitation, MatchPerformance
from api.serializers import PlayerSerializer, TeamSerializer, TeamFullSerializer, UserSerializer, UserProfileSerializer, \
    ChangePasswordSerializer, MemberSerializer, CommentSerializer, MatchSerializer, TeamInvitationSerializer, \
    MatchPerformanceSerializer, MatchFullSerializer, PlayerFullSerializer
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TeamFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)


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

        time = self.request.query_params.get('time')
        if time is not None:
            actual_time = timezone.now()
            if time == "past":
                queryset = queryset.filter(time__lte=actual_time)
            if time == "future":
                queryset = queryset.filter(time__gte=actual_time).order_by('time')

        match_amount = int(self.request.query_params.get('amount', default=5))
        queryset = queryset[:match_amount]
        return queryset


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


class MatchPerformanceViewset(viewsets.ModelViewSet):
    queryset = MatchPerformance.objects.all()
    serializer_class = MatchPerformanceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = MatchPerformance.objects.all()

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

    @action(methods=['GET'], detail=False)
    def get_avg_team_performance(self, request):
        team_id = self.request.query_params.get('team')
        if team_id is not None:
            queryset = MatchPerformance.objects.all()
            queryset = queryset.filter(team=team_id)

            # works for performances not matches
            performances_amount = self.request.query_params.get('amount')
            if performances_amount is not None:
                queryset = queryset[:int(performances_amount)]

            results = self.calculate_avg(queryset)

            response = {'message': 'Successfully calculated', 'results': results}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def calculate_avg(self, queryset):
        queryset_length = len(queryset)
        serve = queryset.aggregate(Sum('serve'))['serve__sum']
        serve_error = queryset.aggregate(Sum('serve_error'))['serve_error__sum']
        serve_ace = queryset.aggregate(Sum('serve_ace'))['serve_ace__sum']
        reception = queryset.aggregate(Sum('reception'))['reception__sum']
        positive_reception = queryset.aggregate(Sum('positive_reception'))['positive_reception__sum']
        reception_error = queryset.aggregate(Sum('reception_error'))['reception_error__sum']
        spike = queryset.aggregate(Sum('spike'))['spike__sum']
        spike_point = queryset.aggregate(Sum('spike_point'))['spike_point__sum']
        spike_block = queryset.aggregate(Sum('spike_block'))['spike_block__sum']
        spike_error = queryset.aggregate(Sum('spike_error'))['spike_error__sum']
        block_amount = queryset.aggregate(Sum('block_amount'))['block_amount__sum']
        dig = queryset.aggregate(Sum('dig'))['dig__sum']

        total_score = spike_point + serve_ace + block_amount
        total_score_balance = total_score - serve_error - reception_error - spike_error - spike_block
        positive_reception_percentage = round((positive_reception / reception) * 100)
        spike_kill_percentage = round((spike_point / spike) * 100)
        spike_efficiency = round(((spike_point - spike_error - spike_block) / spike) * 100)

        results = {
            'total_score': total_score / queryset_length,
            'total_score_balance': total_score_balance / queryset_length,
            'serve': serve / queryset_length,
            'serve_error': serve_error / queryset_length,
            'serve_ace': serve_ace / queryset_length,
            'reception': reception / queryset_length,
            'positive_reception': positive_reception / queryset_length,
            'reception_error': reception_error / queryset_length,
            'positive_reception_percentage': positive_reception_percentage,
            'spike': spike / queryset_length,
            'spike_point': spike_point / queryset_length,
            'spike_block': spike_block / queryset_length,
            'spike_error': spike_error / queryset_length,
            'spike_kill_percentage': spike_kill_percentage,
            'spike_efficiency': spike_efficiency,
            'block_amount': block_amount / queryset_length,
            'dig': dig / queryset_length,
        }
        return results
