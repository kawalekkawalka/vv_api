from django.contrib import admin

from api.models import Player, Team, PlayerMembership, UserProfile, Comment, Match, TeamInvitation


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
    fields = ('name', 'description', 'owner')
    list_display = ('id', 'name', 'description', 'owner')


@admin.register(PlayerMembership)
class MemberAdmin(admin.ModelAdmin):
    fields = ('player', 'team', 'date_left')
    list_display = ('id', 'player', 'team', 'date_joined', 'date_left')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fields = ('user', 'description', 'content_type', 'object_id')
    list_display = ('user', 'time', 'description', 'content_type', 'object_id')


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    fields = ('user', 'team')
    list_display = ('user', 'team')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    fields = ('team1', 'team2', 'time', 'set1_team1_score', 'set2_team1_score', 'set3_team1_score', 'set4_team1_score',
              'set5_team1_score', 'set1_team2_score', 'set2_team2_score', 'set3_team2_score', 'set4_team2_score',
              'set5_team2_score')
    list_display = ('id', 'team1', 'team2', 'time', 'set1_team1_score', 'set2_team1_score', 'set3_team1_score',
                    'set4_team1_score', 'set5_team1_score', 'set1_team2_score', 'set2_team2_score', 'set3_team2_score',
                    'set4_team2_score', 'set5_team2_score')