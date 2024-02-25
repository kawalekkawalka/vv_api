from operator import attrgetter

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Player
from api.serializers.serializers import PlayerSerializer, PlayerFullSerializer, MatchSerializer, MatchFullSerializer
from api.tests.factories import UserFactory, PlayerFactory, MatchFactory


class TestMatchViewset(APITestCase):
    def setUp(self):
        self.matches = MatchFactory.create_batch(size=10)

    def test_list_matches(self):
        sorted_matches = sorted(self.matches, key=lambda match: match.time, reverse=True)

        response = self.client.get('/api/matches/', format='json')
        expected_response = [MatchSerializer(match).data for match in sorted_matches]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, expected_response)

    def test_retrieve_match(self):
        response = self.client.get('/api/matches/' + str(self.matches[0].id) + '/', format='json')
        expected_response = MatchFullSerializer(self.matches[0]).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

