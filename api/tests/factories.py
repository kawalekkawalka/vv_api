import factory
from django.contrib.auth.models import User
from factory.faker import Faker
from api.models import Player, Team, PlayerMembership


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class PlayerFactory(factory.django.DjangoModelFactory):
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


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Faker('company')
    description = factory.Faker('text')
    owner = factory.SubFactory(UserFactory)


class PlayerMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlayerMembership

    player = factory.SubFactory(PlayerFactory)
    team = factory.SubFactory(TeamFactory)
    date_joined = factory.Faker('date_this_decade')
    date_left = factory.Faker('date_this_decade', before_now=True)
