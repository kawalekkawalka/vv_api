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
        ("S", "Rozgrywający"),
        ("OH", "Przyjmujący"),
        ("OP", "Atakujący"),
        ("MB", "Środkowy"),
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

    def __str__(self):
        return self.name


class PlayerMembership(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    date_left = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = (('player', 'team'),)
