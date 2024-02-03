from rest_framework import serializers

from api.models import PlayerRecords
from api.serializers.serializers import MatchSerializer


class PlayerRecordsSerializer(serializers.ModelSerializer):
    serve = serializers.SerializerMethodField()
    serve_error = serializers.SerializerMethodField()
    serve_ace = serializers.SerializerMethodField()
    reception = serializers.SerializerMethodField()
    positive_reception = serializers.SerializerMethodField()
    reception_error = serializers.SerializerMethodField()
    spike = serializers.SerializerMethodField()
    spike_point = serializers.SerializerMethodField()
    block_amount = serializers.SerializerMethodField()
    dig = serializers.SerializerMethodField()

    def get_serve(self, obj):
        return {
            'amount': obj.serve,
            'match': MatchSerializer(obj.serve_match).data if obj.serve_match is not None else None
        }

    def get_serve_error(self, obj):
        return {
            'amount': obj.serve_error,
            'match': MatchSerializer(obj.serve_error_match).data if obj.serve_error_match is not None else None
        }

    def get_serve_ace(self, obj):
        return {
            'amount': obj.serve_ace,
            'match': MatchSerializer(obj.serve_ace_match).data if obj.serve_ace_match is not None else None
        }

    def get_reception(self, obj):
        return {
            'amount': obj.reception,
            'match': MatchSerializer(obj.reception_match).data if obj.reception_match is not None else None
        }

    def get_positive_reception(self, obj):
        return {
            'amount': obj.positive_reception,
            'match': MatchSerializer(obj.positive_reception_match).data if obj.positive_reception_match is not None else None
        }

    def get_reception_error(self, obj):
        return {
            'amount': obj.reception_error,
            'match': MatchSerializer(obj.reception_error_match).data if obj.reception_error_match is not None else None
        }

    def get_spike(self, obj):
        return {
            'amount': obj.spike,
            'match': MatchSerializer(obj.spike_match).data if obj.spike_match is not None else None
        }

    def get_spike_point(self, obj):
        return {
            'amount': obj.spike_point,
            'match': MatchSerializer(obj.spike_point_match).data if obj.spike_point_match is not None else None
        }

    def get_block_amount(self, obj):
        return {
            'amount': obj.block_amount,
            'match': MatchSerializer(obj.block_amount_match).data if obj.block_amount_match is not None else None
        }

    def get_dig(self, obj):
        return {
            'amount': obj.dig,
            'match': MatchSerializer(obj.dig_match).data if obj.dig_match is not None else None
        }

    class Meta:
        model = PlayerRecords
        fields = ('serve', 'serve_error', 'serve_ace', 'reception', 'positive_reception', 'reception_error',
                  'spike', 'spike_point', 'block_amount', 'dig')
