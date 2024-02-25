from rest_framework.test import APITestCase
from rest_framework import status
from api.serializers.serializers import PlayerSerializer, PlayerFullSerializer, MatchSerializer, MatchFullSerializer, \
    TeamInvitationSerializer, UserFriendshipSerializer
from api.tests.factories import UserFactory, PlayerFactory, MatchFactory, MatchPerformanceFactory, \
    TeamInvitationFactory, UserProfileFactory, UserFriendshipFactory


class TestTeamInvitationViewset(APITestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        UserProfileFactory(user=self.user1)
        UserProfileFactory(user=self.user2)
        UserProfileFactory(user=self.user3)
        self.friendship1 = UserFriendshipFactory(user1=self.user1, user2=self.user2)
        self.friendship2 = UserFriendshipFactory(user1=self.user1, user2=self.user3)
        self.friendship3 = UserFriendshipFactory(user1=self.user2, user2=self.user3)

    def test_list_user_friendships(self):
        response = self.client.get('/api/user-friendships/', format='json')
        expected_response = UserFriendshipSerializer((self.friendship1, self.friendship2, self.friendship3),
                                                     many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, expected_response)
