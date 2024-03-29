from django.contrib import admin

from api.models import Player, Team, PlayerMembership, UserProfile, Comment, Match, TeamInvitation, MatchPerformance, \
    PlayerRecords, UserFriendship, UserFriendshipInvitation


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


@admin.register(MatchPerformance)
class MatchPerformanceAdmin(admin.ModelAdmin):
    fields = ('player', 'match', 'team', 'set1_position', 'set2_position', 'set3_position', 'set4_position',
              'set5_position', 'serve', 'serve_error', 'serve_ace', 'reception', 'positive_reception',
              'reception_error', 'spike', 'spike_point', 'spike_block', 'spike_error', 'block_amount', 'dig',)
    list_display = ('id', 'player', 'match', 'team', 'set1_position', 'set2_position', 'set3_position', 'set4_position'
                    , 'set5_position', 'serve', 'serve_error', 'serve_ace', 'reception', 'positive_reception',
                    'reception_error', 'spike', 'spike_point', 'spike_block', 'spike_error', 'block_amount', 'dig',)


@admin.register(PlayerRecords)
class PlayerRecordsAdmin(admin.ModelAdmin):
    fields = ('player', 'serve', 'serve_match', 'serve_error', 'serve_error_match', 'serve_ace', 'serve_ace_match',
              'reception', 'reception_match', 'positive_reception', 'positive_reception_match', 'reception_error',
              'reception_error_match', 'spike', 'spike_match', 'spike_point', 'spike_point_match', 'block_amount',
              'block_amount_match', 'dig', 'dig_match',)

    list_display = ('id', 'player', 'serve', 'serve_match', 'serve_error', 'serve_error_match', 'serve_ace',
                    'serve_ace_match', 'reception', 'reception_match', 'positive_reception', 'positive_reception_match',
                    'reception_error', 'reception_error_match', 'spike', 'spike_match', 'spike_point',
                    'spike_point_match', 'block_amount', 'block_amount_match', 'dig', 'dig_match',)


@admin.register(UserFriendship)
class UserFriendshipAdmin(admin.ModelAdmin):
    fields = ('user1', 'user2')
    list_display = ('user1', 'user2')


@admin.register(UserFriendshipInvitation)
class UserFriendshipInvitationAdmin(admin.ModelAdmin):
    fields = ('inviter', 'invitee')
    list_display = ('inviter', 'invitee')
