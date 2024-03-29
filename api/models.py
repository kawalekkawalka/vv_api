from abc import ABC

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.conf import settings
import io


def upload_path_handler(instance, filename):
    return "avatars/{id}/{file}".format(id=instance.id, file=filename)


class Player(models.Model):
    POSITIONS = [
        ("L", "Libero"),
        ("S", "Setter"),
        ("OH", "Outside hitter"),
        ("OP", "Opposite hitter"),
        ("MB", "Middle blocker"),
    ]
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    nick = models.CharField(max_length=32, blank=True)
    year_of_birth = models.DecimalField(max_digits=4, decimal_places=0)
    height = models.DecimalField(max_digits=3, decimal_places=0)
    weight = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    position = models.CharField(max_length=2, choices=POSITIONS)
    photo = models.ImageField(upload_to=upload_path_handler, default=settings.MEDIA_ROOT + "/avatars/user.png",
                              null=True, blank=True)

    def __str__(self):
        return self.name + " " + self.surname

    @property
    def get_photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        else:
            return "/avatars/user.png"


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    player = models.OneToOneField(Player, related_name='player_profile', on_delete=models.CASCADE)


class Team(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    players = models.ManyToManyField(Player, through="PlayerMembership", through_fields=("team", "player"))
    owner = models.ForeignKey(User, related_name='teams', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PlayerMembership(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    date_left = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = (('player', 'team'),)


class Comment(models.Model):
    user = models.ForeignKey(User, related_name='user_comments', on_delete=models.CASCADE)
    description = models.TextField(max_length=512)
    time = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Match(models.Model):
    team1 = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    time = models.DateTimeField()
    set1_team1_score = models.PositiveSmallIntegerField(default=0)
    set2_team1_score = models.PositiveSmallIntegerField(default=0)
    set3_team1_score = models.PositiveSmallIntegerField(default=0)
    set4_team1_score = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    set5_team1_score = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    set1_team2_score = models.PositiveSmallIntegerField(default=0)
    set2_team2_score = models.PositiveSmallIntegerField(default=0)
    set3_team2_score = models.PositiveSmallIntegerField(default=0)
    set4_team2_score = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    set5_team2_score = models.PositiveSmallIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.team1) + ' vs ' + str(self.team2)


class TeamInvitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'team'),)


class MatchPerformance(models.Model):
    CHOICES = [
        (1, 'Position 1'),
        (2, 'Position 2'),
        (3, 'Position 3'),
        (4, 'Position 4'),
        (5, 'Position 5'),
        (6, 'Position 6'),
        (7, 'Libero'),
        (8, 'Substitution')]
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    set1_position = models.PositiveSmallIntegerField(null=True, blank=True, choices=CHOICES)
    set2_position = models.PositiveSmallIntegerField(null=True, blank=True, choices=CHOICES)
    set3_position = models.PositiveSmallIntegerField(null=True, blank=True, choices=CHOICES)
    set4_position = models.PositiveSmallIntegerField(null=True, blank=True, choices=CHOICES)
    set5_position = models.PositiveSmallIntegerField(null=True, blank=True, choices=CHOICES)
    serve = models.PositiveSmallIntegerField(default=0)
    serve_error = models.PositiveSmallIntegerField(default=0)
    serve_ace = models.PositiveSmallIntegerField(default=0)
    reception = models.PositiveSmallIntegerField(default=0)
    positive_reception = models.PositiveSmallIntegerField(default=0)
    reception_error = models.PositiveSmallIntegerField(default=0)
    spike = models.PositiveSmallIntegerField(default=0)
    spike_point = models.PositiveSmallIntegerField(default=0)
    spike_block = models.PositiveSmallIntegerField(default=0)
    spike_error = models.PositiveSmallIntegerField(default=0)
    block_amount = models.PositiveSmallIntegerField(default=0)
    dig = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (('player', 'match'),)


class PlayerRecords(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    serve = models.PositiveSmallIntegerField(default=0)
    serve_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='serve_matches')
    serve_error = models.PositiveSmallIntegerField(default=0)
    serve_error_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='serve_error_matches')
    serve_ace = models.PositiveSmallIntegerField(default=0)
    serve_ace_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='serve_ace_matches')
    reception = models.PositiveSmallIntegerField(default=0)
    reception_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='reception_matches')
    positive_reception = models.PositiveSmallIntegerField(default=0)
    positive_reception_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                                 related_name='positive_reception_matches')
    reception_error = models.PositiveSmallIntegerField(default=0)
    reception_error_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                              related_name='reception_error_matches')
    spike = models.PositiveSmallIntegerField(default=0)
    spike_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='spike_matches')
    spike_point = models.PositiveSmallIntegerField(default=0)
    spike_point_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='spike_point_matches')
    block_amount = models.PositiveSmallIntegerField(default=0)
    block_amount_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='block_amount_matches')
    dig = models.PositiveSmallIntegerField(default=0)
    dig_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='dig_matches')


class UserFriendship(models.Model):
    user1 = models.ForeignKey(User, related_name='user1_friendships', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='user2_friendships',  on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user1', 'user2'),)


class UserFriendshipInvitation(models.Model):
    inviter = models.ForeignKey(User, related_name='invitations', on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, related_name='invited_users',  on_delete=models.CASCADE)

    class Meta:
        unique_together = (('inviter', 'invitee'),)
