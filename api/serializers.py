from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from api.models import Player, Team, PlayerMembership, UserProfile, Comment


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ('id', 'name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position', 'photo')
        extra_kwargs = {'name': {'required': False}, 'surname': {'required': False}, 'height': {'required': False},
                        'year_of_birth': {'required': False}, 'position': {'required': False}}


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
        fields = ('id', 'name', 'description')


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
        fields = ('id', 'name', 'description', 'players', 'comments')

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
        comments = Comment.objects.filter(object_id=obj.id)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data
