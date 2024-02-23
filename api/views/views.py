from datetime import date
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from api.models import Player, Team, UserProfile, PlayerMembership, Comment, TeamInvitation, PlayerRecords, \
    UserFriendship, UserFriendshipInvitation
from api.serializers.player_records_serializers import PlayerRecordsSerializer
from api.serializers.serializers import PlayerSerializer, UserSerializer, UserProfileSerializer, \
    ChangePasswordSerializer, MemberSerializer, CommentSerializer, TeamInvitationSerializer, \
    PlayerFullSerializer, UserFriendshipSerializer, UserFriendshipInvitationSerializer
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

    def get_queryset(self):
        queryset = Player.objects.all()
        order = self.request.query_params.get('order')
        if order == 'desc':
            queryset = queryset.order_by('-id')
        player_amount = int(self.request.query_params.get('amount', 0))
        if player_amount:
            queryset = queryset[:player_amount]
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PlayerFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
        team_id = self.request.query_params.get('team')
        if team_id is not None:
            return TeamInvitation.objects.filter(team=team_id)
        return TeamInvitation.objects.all()

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


class UserFriendshipViewset(viewsets.ModelViewSet):
    queryset = UserFriendship.objects.all()
    serializer_class = UserFriendshipSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):

        return UserFriendship.objects.all()

    @action(methods=['GET'], detail=False)
    def get_user_friends(self, request):
        user_id = self.request.query_params.get('user')
        if user_id is not None:
            friendships = UserFriendship.objects.filter(Q(user1=user_id) | Q(user2=user_id)).values_list('user1',
                                                                                                         'user2')
            friends_id = set()
            for friendship in friendships:
                friends_id.add(friendship[0])
                friends_id.add(friendship[1])
            friends_id.remove(int(user_id))
            friends_queryset = User.objects.filter(id__in=friends_id)
            return Response(UserSerializer(friends_queryset, many=True).data, status=status.HTTP_200_OK)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['DELETE'], detail=False, permission_classes=(IsAuthenticated,))
    def delete_friend(self, request):
        try:
            friendship = UserFriendship.objects.get(
                Q(user1=request.data['user1'], user2=request.data['user2']) |
                Q(user1=request.data['user2'], user2=request.data['user1']))
            friendship.delete()
            return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)
        except UserFriendship.DoesNotExist:
            response = {'message': 'Friendship does not exist'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'message': 'Wrong users data'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            user1 = User.objects.get(id=request.data['user1'])
            user2 = User.objects.get(id=request.data['user2'])
            if user1 == user2:
                return Response({'message': 'Users have to be unique'}, status=status.HTTP_400_BAD_REQUEST)

            existing_friendship = UserFriendship.objects.filter(
                (Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1))
            ).first()
            if existing_friendship:
                return Response({'message': 'Friendship already exist'}, status=status.HTTP_200_OK)

            UserFriendship.objects.create(user1=user1, user2=user2)
            return Response({'message': 'Friendship created'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message': 'Provided users not exist'}, status=status.HTTP_400_BAD_REQUEST)


class UserFriendshipInvitationViewset(viewsets.ModelViewSet):
    queryset = UserFriendshipInvitation.objects.all()
    serializer_class = UserFriendshipInvitationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['GET'], detail=False)
    def get_user_friends_invitations(self, request):
        if self.request.query_params.get('user'):
            invitations = UserFriendshipInvitation.objects.filter(
                invitee=self.request.query_params.get('user')).select_related('inviter')
            response = [UserSerializer(invitation.inviter).data for invitation in invitations]
            return Response(response, status=status.HTTP_200_OK)
        return Response({'message': 'Wrong params'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            inviter = User.objects.get(id=request.data['inviter'])
            invitee = User.objects.get(id=request.data['invitee'])
            if inviter == invitee:
                return Response({'message': 'Users have to be unique'}, status=status.HTTP_400_BAD_REQUEST)
            if UserFriendship.objects.filter((Q(user1=inviter, user2=invitee) | Q(user1=invitee, user2=inviter))).first():
                return Response({'message': 'Friendship already exist'}, status=status.HTTP_200_OK)
            if UserFriendshipInvitation.objects.filter(inviter=inviter, invitee=invitee).first():
                return Response({'message': 'Invitation already sent'}, status=status.HTTP_200_OK)
            invitee_invitation = UserFriendshipInvitation.objects.filter(inviter=invitee, invitee=inviter).first()
            if invitee_invitation:
                UserFriendship.objects.create(user1=inviter, user2=invitee)
                invitee_invitation.delete()
                return Response({'message': 'Invitee already invited you. Friendship created'},
                                status=status.HTTP_201_CREATED)
            UserFriendshipInvitation.objects.create(inviter=inviter, invitee=invitee)
            return Response({'message': 'Invitation sent'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message': 'Provided users not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'message': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        response = {'message': 'Method not allowed'}
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['DELETE'], detail=False, permission_classes=(IsAuthenticated,))
    def delete_invitation(self, request):
        try:
            invitation = UserFriendshipInvitation.objects.get(inviter=request.data['inviter'],
                                                              invitee=request.data['invitee'])
            invitation.delete()
            response = {'message': 'Successfully deleted'}
            return Response(response, status=status.HTTP_200_OK)
        except UserFriendshipInvitation.DoesNotExist:
            response = {'message': 'Invitation does not exist'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            response = {'message': 'Bad request'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
