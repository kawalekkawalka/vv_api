from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import Player, Team, PlayerMembership, UserProfile, Comment, Match, TeamInvitation, UserFriendship, \
    UserFriendshipInvitation


class PlayerSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ('id', 'name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position', 'photo', 'photo_url')
        extra_kwargs = {'name': {'required': False}, 'surname': {'required': False}, 'height': {'required': False},
                        'year_of_birth': {'required': False}, 'position': {'required': False},
                        'photo': {'write_only': True}}

    def get_photo_url(self, obj):
        try:
            return obj.get_photo_url
        except KeyError:
            return None


class PlayerFullSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ('id', 'name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position', 'photo_url'
                  , 'comments', 'user', 'friends')

    def get_photo_url(self, obj):
        try:
            return obj.get_photo_url
        except KeyError:
            return None

    def get_comments(self, obj):
        comments = Comment.objects.filter(object_id=obj.id, content_type=9)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    def get_user(self, obj):
        try:
            return obj.player_profile.user.id
        except:
            return None

    def get_friends(self, obj):
        try:
            friends = set()
            friendships = UserFriendship.objects.filter(
                Q(user1=obj.player_profile.user.id) | Q(user2=obj.player_profile.user.id)).values_list('user1', 'user2')
            for friendship in friendships:
                friends.add(friendship[0])
                friends.add(friendship[1])
            friends.remove(obj.player_profile.user.id)
            return friends
        except:
            return []


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'player', 'user')


class UserSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField('get_player_from_profile')

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'player')
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def get_player_from_profile(profile):
        player = PlayerSerializer(profile.profile.player)
        return player.data

    def create(self, validated_data):
        player = self.context['request'].data['player']
        user = User.objects.create_user(**validated_data)
        player = Player.objects.create(**player)
        UserProfile.objects.create(player=player, user=user)
        Token.objects.create(user=user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'owner')


class MemberSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(many=False)
    team = TeamSerializer(many=False)

    class Meta:
        model = PlayerMembership
        fields = ('id', 'player', 'team', 'date_joined', 'date_left')


class CommentSerializer(serializers.ModelSerializer):
    # commented_object = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'description')

    def get_commented_object(self, obj):
        if obj.content_type.model == 'team':
            team = Team.objects.get(pk=obj.object_id)
            serializer = TeamSerializer(team)
        return serializer.data

    def get_user(self, obj):
        user = User.objects.get(pk=obj.user.id)
        serialized_user = UserSerializer(user, many=False)
        return serialized_user.data


class TeamFullSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField('get_active_players')
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'players', 'comments', 'owner')

    def get_active_players(self, obj):
        players = obj.players.all()
        active_players = []
        for player in players:
            player_serialized = PlayerSerializer(player, many=False)
            membership = PlayerMembership.objects.get(player=player_serialized.data.get('id'), team=obj.id)
            membership_serialized = MemberSerializer(membership, many=False)
            date_left = membership_serialized.data.get('date_left')
            if date_left is None:
                active_players.append(player_serialized.data)

        return active_players

    def get_comments(self, obj):
        comments = Comment.objects.filter(object_id=obj.id, content_type=11)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data


class TeamPlayerSerializer(serializers.ModelSerializer):
    date_joined = serializers.SerializerMethodField()
    date_left = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'date_joined', 'date_left')

    def get_date_joined(self, obj):
        player_membership = PlayerMembership.objects.get(player=self.context['player_id'], team=obj.id)
        return player_membership.date_joined

    def get_date_left(self, obj):
        player_membership = PlayerMembership.objects.get(player=self.context['player_id'], team=obj.id)
        return player_membership.date_left


class MatchSerializer(serializers.ModelSerializer):
    team1_name = serializers.SerializerMethodField()
    team2_name = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ('id', 'team1', 'team2', 'team1_name', 'team2_name', 'time', 'set1_team1_score', 'set2_team1_score',
                  'set3_team1_score', 'set4_team1_score', 'set5_team1_score', 'set1_team2_score', 'set2_team2_score',
                  'set3_team2_score', 'set4_team2_score', 'set5_team2_score')

    def get_team1_name(self, obj):
        name = obj.team1.name
        return name

    def get_team2_name(self, obj):
        name = obj.team2.name
        return name


class MatchFullSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer(many=False)
    team2 = TeamSerializer(many=False)
    team1_name = serializers.SerializerMethodField()
    team2_name = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ('id', 'team1', 'team2', 'team1_name', 'team2_name', 'time', 'set1_team1_score', 'set2_team1_score',
                  'set3_team1_score', 'set4_team1_score', 'set5_team1_score', 'set1_team2_score', 'set2_team2_score',
                  'set3_team2_score', 'set4_team2_score', 'set5_team2_score', 'comments')

    def get_team1_name(self, obj):
        name = obj.team1.name
        return name

    def get_team2_name(self, obj):
        name = obj.team2.name
        return name

    def get_comments(self, obj):
        comments = Comment.objects.filter(object_id=obj.id, content_type=14)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data


class TeamInvitationSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = TeamInvitation
        fields = ('id', 'user', 'team')


class UserFriendshipSerializer(serializers.ModelSerializer):
    player1 = serializers.SerializerMethodField()
    player2 = serializers.SerializerMethodField()

    class Meta:
        model = UserFriendship
        fields = ('user1', 'user2', 'player1', 'player2')

    def get_player1(self, obj):
        return PlayerSerializer(obj.user1.profile.player, many=False).data

    def get_player2(self, obj):
        return PlayerSerializer(obj.user2.profile.player, many=False).data


class UserFriendshipInvitationSerializer(serializers.ModelSerializer):
    player1 = serializers.SerializerMethodField()
    player2 = serializers.SerializerMethodField()

    class Meta:
        model = UserFriendshipInvitation
        fields = ('inviter', 'invitee', 'player1', 'player2')

    def get_player1(self, obj):
        return PlayerSerializer(obj.inviter.profile.player, many=False).data

    def get_player2(self, obj):
        return PlayerSerializer(obj.invitee.profile.player, many=False).data
