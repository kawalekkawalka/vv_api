from operator import attrgetter

from rest_framework.test import APITestCase
from rest_framework import status
from api.serializers.serializers import PlayerSerializer, PlayerFullSerializer, MatchSerializer, MatchFullSerializer, \
    TeamInvitationSerializer
from api.tests.factories import UserFactory, PlayerFactory, MatchFactory, MatchPerformanceFactory, \
    TeamInvitationFactory, UserProfileFactory


class TestTeamInvitationViewset(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.profile = UserProfileFactory(user=self.user)
        self.team_invitations = TeamInvitationFactory.create_batch(size=10, user=self.user)

    def test_list_team_performances(self):
        response = self.client.get('/api/team-invitations/', format='json')
        expected_response = TeamInvitationSerializer(self.team_invitations, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, expected_response)
