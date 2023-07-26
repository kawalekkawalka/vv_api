from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from api.models import Player, Team, UserProfile, PlayerMembership
from api.serializers import PlayerSerializer, TeamSerializer, TeamFullSerializer, UserSerializer, UserProfileSerializer, \
    ChangePasswordSerializer, MemberSerializer
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


class MemberViewset(viewsets.ModelViewSet):
    queryset = PlayerMembership.objects.all()
    serializer_class = MemberSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['POST'], detail=False)
    def join(self, request):
        if 'player' in request.data and 'team' in request.data:
            try:
                player = Player.objects.get(id=request.data['player'])
                team = Team.objects.get(id=request.data['team'])
                member = PlayerMembership.objects.create(player=player, team=team)
                serializer = MemberSerializer(member, many=False)
                response = {'message': 'Added to team', 'results': serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)
            except:
                response = {'message': 'Already in team'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {'message': 'Wrong parameters'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def leave(self, request):
        if 'player' in request.data and 'team' in request.data:
            player = Player.objects.get(id=request.data['player'])
            team = Team.objects.get(id=request.data['team'])
            member = PlayerMembership.objects.get(player=player, team=team)
            member.delete()
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


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        user_serializer = UserSerializer(user, many=False)
        return Response({'token': token.key, 'user': user_serializer.data})

