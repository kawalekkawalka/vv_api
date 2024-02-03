from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.models import MatchPerformance, Player, PlayerRecords
from api.serializers.serializers import PlayerSerializer
from api.serializers.match_performance_serializers import MatchPerformanceSerializer, MatchPerformanceCreateSerializer

EMPTY_RESULTS = {
    'total_score': 0,
    'total_score_balance': 0,
    'serve': 0,
    'serve_error': 0,
    'serve_ace': 0,
    'reception': 0,
    'positive_reception': 0,
    'reception_error': 0,
    'positive_reception_percentage': 0,
    'spike': 0,
    'spike_point': 0,
    'spike_block': 0,
    'spike_error': 0,
    'spike_kill_percentage': 0,
    'spike_efficiency': 0,
    'block_amount': 0,
    'dig': 0,
}


class MatchPerformanceViewset(viewsets.ModelViewSet):
    queryset = MatchPerformance.objects.all()
    serializer_class = MatchPerformanceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = MatchPerformance.objects.all()

        player_id = self.request.query_params.get('player')
        if player_id is not None:
            queryset = queryset.filter(player=player_id)

        team_id = self.request.query_params.get('team')
        if team_id is not None:
            queryset = queryset.filter(team=team_id)

        match_id = self.request.query_params.get('match')
        if match_id is not None:
            queryset = queryset.filter(match=match_id)

        match_performances_amount = int(self.request.query_params.get('amount', default=100))
        queryset = queryset[:match_performances_amount]
        return queryset

    @action(methods=['GET'], detail=False)
    def get_avg_team_performance(self, request):
        team_id = self.request.query_params.get('team')
        if team_id is not None:
            queryset = MatchPerformance.objects.all()
            queryset = queryset.filter(team=team_id)

            # works for performances not matches
            performances_amount = self.request.query_params.get('amount')
            if performances_amount is not None:
                queryset = queryset[:int(performances_amount)]

            results = self.calculate_avg(queryset, len(queryset))

            response = {'message': 'Successfully calculated', 'results': results}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False)
    def get_avg_player_performance(self, request):
        player_id = self.request.query_params.get('player')
        team_id = self.request.query_params.get('team')
        if player_id is not None:
            player = Player.objects.get(id=player_id)
            if team_id is not None:
                queryset = MatchPerformance.objects.filter(player=player, team=team_id)
            else:
                queryset = MatchPerformance.objects.filter(player=player)
            if not queryset.exists():
                response = {'message': 'Player has no performances', 'results': EMPTY_RESULTS, 'set_amount': 0,
                            'player': PlayerSerializer(player).data}
                return Response(response, status=status.HTTP_200_OK)
            queryset = queryset.order_by("-match__time")

            performances_amount = self.request.query_params.get('amount')
            if performances_amount is not None:
                queryset = queryset[:int(performances_amount)]

            set_amount = self.count_sets(queryset)
            results = self.calculate_avg(queryset, set_amount)

            response = {'message': 'Successfully calculated', 'results': results, 'set_amount': set_amount,
                        'player': PlayerSerializer(player).data}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = MatchPerformanceCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.update_player_record(performance=serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def count_sets(self, queryset):
        set_amount = 0
        for performance in queryset:
            for i in range(5):
                set_position_attr = f"set{i + 1}_position"
                if getattr(performance, set_position_attr, None):
                    set_amount += 1
        return set_amount

    def calculate_avg(self, queryset, divider):
        serve = queryset.aggregate(Sum('serve'))['serve__sum']
        serve_error = queryset.aggregate(Sum('serve_error'))['serve_error__sum']
        serve_ace = queryset.aggregate(Sum('serve_ace'))['serve_ace__sum']
        reception = queryset.aggregate(Sum('reception'))['reception__sum']
        positive_reception = queryset.aggregate(Sum('positive_reception'))['positive_reception__sum']
        reception_error = queryset.aggregate(Sum('reception_error'))['reception_error__sum']
        spike = queryset.aggregate(Sum('spike'))['spike__sum']
        spike_point = queryset.aggregate(Sum('spike_point'))['spike_point__sum']
        spike_block = queryset.aggregate(Sum('spike_block'))['spike_block__sum']
        spike_error = queryset.aggregate(Sum('spike_error'))['spike_error__sum']
        block_amount = queryset.aggregate(Sum('block_amount'))['block_amount__sum']
        dig = queryset.aggregate(Sum('dig'))['dig__sum']

        total_score = spike_point + serve_ace + block_amount
        total_score_balance = total_score - serve_error - reception_error - spike_error - spike_block
        if reception:
            positive_reception_percentage = round((positive_reception / reception) * 100)
        else:
            positive_reception_percentage = 0
        if spike:
            spike_kill_percentage = round((spike_point / spike) * 100)
            spike_efficiency = round(((spike_point - spike_error - spike_block) / spike) * 100)
        else:
            spike_kill_percentage = 0
            spike_efficiency = 0

        results = {
            'total_score': round(total_score / divider, 2),
            'total_score_balance': round(total_score_balance / divider, 2),
            'serve': round(serve / divider, 2),
            'serve_error': round(serve_error / divider, 2),
            'serve_ace': round(serve_ace / divider, 2),
            'reception': round(reception / divider, 2),
            'positive_reception': round(positive_reception / divider, 2),
            'reception_error': round(reception_error / divider, 2),
            'positive_reception_percentage': round(positive_reception_percentage, 2),
            'spike': round(spike / divider, 2),
            'spike_point': round(spike_point / divider, 2),
            'spike_block': round(spike_block / divider, 2),
            'spike_error': round(spike_error / divider, 2),
            'spike_kill_percentage': round(spike_kill_percentage, 2),
            'spike_efficiency': round(spike_efficiency, 2),
            'block_amount': round(block_amount / divider, 2),
            'dig': round(dig / divider, 2),
        }

        return results

    def update_player_record(self, performance):
        player_record = PlayerRecords.objects.filter(player=performance.get('player')).first()
        match = performance.get('match')
        if not player_record:
            player_record = PlayerRecords.objects.create(player=performance.get('player'))
        if performance.get('serve', 0) > player_record.serve:
            player_record.serve = performance['serve']
            player_record.serve_match = match

        if performance.get('serve_error', 0) > player_record.serve_error:
            player_record.serve_error = performance['serve_error']
            player_record.serve_error_match = match

        if performance.get('serve_ace', 0) > player_record.serve_ace:
            player_record.serve_ace = performance['serve_ace']
            player_record.serve_ace_match = match

        if performance.get('reception', 0) > player_record.reception:
            player_record.reception = performance['reception']
            player_record.reception_match = match

        if performance.get('positive_reception', 0) > player_record.positive_reception:
            player_record.positive_reception = performance['positive_reception']
            player_record.positive_reception_match = match

        if performance.get('reception_error', 0) > player_record.reception_error:
            player_record.reception_error = performance['reception_error']
            player_record.reception_error_match = match

        if performance.get('spike', 0) > player_record.spike:
            player_record.spike = performance['spike']
            player_record.spike_match = match

        if performance.get('spike_point', 0) > player_record.spike_point:
            player_record.spike_point = performance['spike_point']
            player_record.spike_point_match = match

        if performance.get('block_amount', 0) > player_record.block_amount:
            player_record.block_amount = performance['block_amount']
            player_record.block_amount_match = match

        if performance.get('dig', 0) > player_record.dig:
            player_record.dig = performance['dig']
            player_record.dig_match = match

        player_record.save()
