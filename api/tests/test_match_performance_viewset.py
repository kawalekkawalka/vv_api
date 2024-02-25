from operator import attrgetter

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Player
from api.serializers.match_performance_serializers import MatchPerformanceSerializer
from api.serializers.serializers import PlayerSerializer, PlayerFullSerializer, MatchSerializer, MatchFullSerializer
from api.tests.factories import UserFactory, PlayerFactory, MatchFactory, MatchPerformanceFactory


class TestMatchPerformanceViewset(APITestCase):
    def setUp(self):
        self.performances = MatchPerformanceFactory.create_batch(size=10)

    def test_list_performances(self):
        response = self.client.get('/api/match-performances/', format='json')
        expected_response = MatchPerformanceSerializer(self.performances, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, expected_response)

    def test_retrieve_match_performance(self):
        response = self.client.get('/api/match-performances/' + str(self.performances[0].id) + '/', format='json')
        expected_response = MatchPerformanceSerializer(self.performances[0]).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

