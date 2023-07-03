from django.contrib import admin

from api.models import Player, Team, PlayerMembership


class PlayerMembershipInline(admin.TabularInline):
    model = PlayerMembership
    extra = 1


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    fields = ('name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position')
    list_display = ('id', 'name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = [PlayerMembershipInline]
    fields = ('name', 'description')
    list_display = ('id', 'name', 'description')
