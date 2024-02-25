import factory
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from factory.faker import Faker
from factory.django import DjangoModelFactory
from api.models import *


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class PlayerFactory(DjangoModelFactory):
    class Meta:
        model = Player

    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    nick = factory.Faker('user_name')
    year_of_birth = factory.Faker('random_int', min=1950, max=2010)
    height = factory.Faker('random_int', min=150, max=220)
    weight = factory.Faker('random_int', min=50, max=120)
    position = factory.Faker('random_element', elements=['L', 'S', 'OH', 'OP', 'MB'])
    photo = factory.django.ImageField(color='blue')


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Faker('company')
    description = factory.Faker('text')
    owner = factory.SubFactory(UserFactory)


class PlayerMembershipFactory(DjangoModelFactory):
    class Meta:
        model = PlayerMembership

    player = factory.SubFactory(PlayerFactory)
    team = factory.SubFactory(TeamFactory)
    date_joined = factory.Faker('date_this_decade')
    date_left = factory.Faker('date_this_decade', before_now=True)


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    player = factory.SubFactory(PlayerFactory)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    user = factory.SubFactory(UserFactory)
    description = factory.Faker('text', max_nb_chars=512)
    time = factory.LazyFunction(timezone.now)
    content_type = factory.LazyAttribute(lambda x: ContentType.objects.get_for_model(x.object))
    object_id = factory.Sequence(lambda n: n)
    content_object = GenericForeignKey('content_type', 'object_id')


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    team1 = factory.SubFactory(TeamFactory)
    team2 = factory.SubFactory(TeamFactory)
    time = factory.LazyFunction(timezone.now)
    set1_team1_score = factory.Faker('pyint', min_value=0, max_value=25)
    set2_team1_score = factory.Faker('pyint', min_value=0, max_value=25)
    set3_team1_score = factory.Faker('pyint', min_value=0, max_value=25)
    set4_team1_score = factory.Faker('pyint', min_value=0, max_value=25)
    set5_team1_score = factory.Faker('pyint', min_value=0, max_value=25)
    set1_team2_score = factory.Faker('pyint', min_value=0, max_value=25)
    set2_team2_score = factory.Faker('pyint', min_value=0, max_value=25)
    set3_team2_score = factory.Faker('pyint', min_value=0, max_value=25)
    set4_team2_score = factory.Faker('pyint', min_value=0, max_value=25)
    set5_team2_score = factory.Faker('pyint', min_value=0, max_value=25)


class TeamInvitationFactory(DjangoModelFactory):
    class Meta:
        model = TeamInvitation

    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)


class MatchPerformanceFactory(DjangoModelFactory):
    class Meta:
        model = MatchPerformance

    player = factory.SubFactory(PlayerFactory)
    match = factory.SubFactory(MatchFactory)
    team = factory.SubFactory(TeamFactory)
    set1_position = factory.Faker('random_element', elements=[1, 2, 3, 4, 5, 6, 7, 8])
    set2_position = factory.Faker('random_element', elements=[1, 2, 3, 4, 5, 6, 7, 8])
    set3_position = factory.Faker('random_element', elements=[1, 2, 3, 4, 5, 6, 7, 8])
    set4_position = factory.Faker('random_element', elements=[1, 2, 3, 4, 5, 6, 7, 8])
    set5_position = factory.Faker('random_element', elements=[1, 2, 3, 4, 5, 6, 7, 8])
    serve = factory.Faker('pyint', min_value=0, max_value=10)
    serve_error = factory.Faker('pyint', min_value=0, max_value=10)
    serve_ace = factory.Faker('pyint', min_value=0, max_value=10)
    reception = factory.Faker('pyint', min_value=0, max_value=10)
    positive_reception = factory.Faker('pyint', min_value=0, max_value=10)
    reception_error = factory.Faker('pyint', min_value=0, max_value=10)
    spike = factory.Faker('pyint', min_value=0, max_value=10)
    spike_point = factory.Faker('pyint', min_value=0, max_value=10)
    spike_block = factory.Faker('pyint', min_value=0, max_value=10)
    spike_error = factory.Faker('pyint', min_value=0, max_value=10)
    block_amount = factory.Faker('pyint', min_value=0, max_value=10)
    dig = factory.Faker('pyint', min_value=0, max_value=10)


class PlayerRecordsFactory(DjangoModelFactory):
    class Meta:
        model = PlayerRecords

    player = factory.SubFactory(PlayerFactory)
    serve = factory.Faker('pyint', min_value=0, max_value=10)
    serve_match = factory.SubFactory(MatchFactory)
    serve_error = factory.Faker('pyint', min_value=0, max_value=10)
    serve_error_match = factory.SubFactory(MatchFactory)
    serve_ace = factory.Faker('pyint', min_value=0, max_value=10)
    serve_ace_match = factory.SubFactory(MatchFactory)
    reception = factory.Faker('pyint', min_value=0, max_value=10)
    reception_match = factory.SubFactory(MatchFactory)
    positive_reception = factory.Faker('pyint', min_value=0, max_value=10)
    positive_reception_match = factory.SubFactory(MatchFactory)
    reception_error = factory.Faker('pyint', min_value=0, max_value=10)
    reception_error_match = factory.SubFactory(MatchFactory)
    spike = factory.Faker('pyint', min_value=0, max_value=10)
    spike_match = factory.SubFactory(MatchFactory)
    spike_point = factory.Faker('pyint', min_value=0, max_value=10)
    spike_point_match = factory.SubFactory(MatchFactory)
    block_amount = factory.Faker('pyint', min_value=0, max_value=10)
    block_amount_match = factory.SubFactory(MatchFactory)
    dig = factory.Faker('pyint', min_value=0, max_value=10)
    dig_match = factory.SubFactory(MatchFactory)


class UserFriendshipFactory(DjangoModelFactory):
    class Meta:
        model = UserFriendship

    user1 = factory.SubFactory(UserFactory)
    user2 = factory.SubFactory(UserFactory)


class UserFriendshipInvitationFactory(DjangoModelFactory):
    class Meta:
        model = UserFriendshipInvitation

    inviter = factory.SubFactory(UserFactory)
    invitee = factory.SubFactory(UserFactory)