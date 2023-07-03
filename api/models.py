from django.db import models


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

    def __str__(self):
        return self.name + " " + self.surname
    # membership w druztnie
    # account powinno miec klucz obcy do player


class Team(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    players = models.ManyToManyField(Player, through="PlayerMembership")

    def __str__(self):
        return self.name


class PlayerMembership(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    date_left = models.DateField(null=True, blank=True)
