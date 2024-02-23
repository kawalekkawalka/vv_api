import json
from json import loads
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from api.tests.factories import TeamFactory, UserFactory


class TestTeamViewset(APITestCase):
    def test_successful_request(self):
        teams = TeamFactory.create_batch(size=5)
        expected_response = [{
            'id': team.id,
            'name': team.name,
            'description': team.description,
            'owner': team.owner.id
        } for team in teams
        ]
        response = self.client.get('/api/teams/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(loads(response.content), expected_response)

    def test_get_teams_names(self):
        teams = TeamFactory.create_batch(size=5)
        expected_response = [team.name for team in teams]
        response = self.client.get('/api/teams/get_teams_names/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(loads(response.content), expected_response)

    def test_delete_not_owned_team(self):
        team = TeamFactory()
        user = UserFactory(username='testuser', password='testpassword')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.delete('/api/teams/' + str(team.id) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You are not owner of the team')
