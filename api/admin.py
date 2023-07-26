from django.contrib import admin

from api.models import Player, Team, PlayerMembership, UserProfile


class PlayerMembershipInline(admin.TabularInline):
    model = PlayerMembership
    extra = 1


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    fields = ('name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position', 'photo')
    list_display = ('id', 'name', 'surname', 'nick', 'year_of_birth', 'height', 'weight', 'position')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'player')
    list_display = ('id', 'user', 'player')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = [PlayerMembershipInline]
    fields = ('name', 'description')
    list_display = ('id', 'name', 'description')


@admin.register(PlayerMembership)
class MemberAdmin(admin.ModelAdmin):
    fields = ('player', 'team', 'date_left')
    list_display = ('id', 'player', 'team', 'date_joined', 'date_left')
