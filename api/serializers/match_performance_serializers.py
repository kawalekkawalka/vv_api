from rest_framework import serializers

from api.models import MatchPerformance
from api.serializers.serializers import MatchSerializer, TeamSerializer, PlayerSerializer


class MatchPerformanceSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()
    match = MatchSerializer(many=False)
    team = TeamSerializer(many=False)
    total_score = serializers.SerializerMethodField()
    total_score_balance = serializers.SerializerMethodField()
    positive_reception_percentage = serializers.SerializerMethodField()
    spike_kill_percentage = serializers.SerializerMethodField()
    spike_efficiency = serializers.SerializerMethodField()

    class Meta:
        model = MatchPerformance
        fields = ('id', 'player', 'match', 'team', 'set1_position', 'set2_position', 'set3_position', 'set4_position',
                  'set5_position', 'total_score', 'total_score_balance', 'serve', 'serve_error', 'serve_ace',
                  'reception', 'positive_reception', 'reception_error', 'positive_reception_percentage', 'spike',
                  'spike_point', 'spike_block', 'spike_error', 'spike_kill_percentage', 'spike_efficiency',
                  'block_amount', 'dig',)

    def get_player(self, obj):
        player = PlayerSerializer(obj.player)
        return player.data

    def get_total_score(self, obj):
        return obj.serve_ace + obj.spike_point + obj.block_amount

    def get_total_score_balance(self, obj):
        return obj.serve_ace + obj.spike_point + obj.block_amount - obj.serve_error - obj.reception_error - \
            obj.spike_error - obj.spike_block

    def get_positive_reception_percentage(self, obj):
        if obj.reception != 0:
            return round((obj.positive_reception / obj.reception) * 100)
        else:
            return 0

    def get_spike_kill_percentage(self, obj):
        if obj.spike != 0:
            return round((obj.spike_point / obj.spike) * 100)
        else:
            return 0

    def get_spike_efficiency(self, obj):
        if obj.spike != 0:
            return round(((obj.spike_point - obj.spike_error - obj.spike_block) / obj.spike) * 100)
        else:
            return 0


class MatchPerformanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPerformance
        fields = '__all__'

    def validate(self, data):
        return data
