from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.models import MatchPerformance
from api.serializers import MatchPerformanceSerializer


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
        if player_id is not None:
            queryset = MatchPerformance.objects.all()
            queryset = queryset.filter(player=player_id)
            if not queryset.exists():
                response = {'message': 'Player has no performances'}
                return Response(response, status=status.HTTP_200_OK)
            queryset = queryset.order_by("-match__time")

            performances_amount = self.request.query_params.get('amount')
            if performances_amount is not None:
                queryset = queryset[:int(performances_amount)]

            set_amount = self.count_sets(queryset)
            results = self.calculate_avg(queryset, set_amount)

            response = {'message': 'Successfully calculated', 'results': results, 'set_amount': set_amount}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'message': 'Wrong params'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

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
