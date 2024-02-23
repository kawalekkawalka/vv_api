from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Player
from api.serializers.serializers import PlayerSerializer, PlayerFullSerializer
from api.tests.factories import UserFactory, PlayerFactory


class TestPlayerViewset(APITestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()

        self.players = PlayerFactory.create_batch(size=10)

    def test_list_players(self):
        response = self.client.get('/api/players/', format='json')
        expected_response = [PlayerSerializer(player).data for player in self.players]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_list_players_with_order(self):
        response = self.client.get('/api/players/' + '?order=desc', format='json')
        expected_response = [PlayerSerializer(player).data for player in reversed(self.players)]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_list_players_with_amount(self):
        response = self.client.get('/api/players/' + '?amount=1', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_player(self):
        response = self.client.get('/api/players/' + str(self.players[0].id) + '/', format='json')
        expected_response = PlayerFullSerializer(self.players[0]).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

