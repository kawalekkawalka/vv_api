from django.urls import re_path

from api import views
from rest_framework import routers
from django.conf.urls import include

router = routers.DefaultRouter()
router.register(r'players', views.PlayerViewset)
router.register(r'teams', views.TeamViewset)
router.register(r'users', views.UserViewset)
router.register(r'members', views.MemberViewset)
router.register(r'comments', views.CommentViewset)
router.register(r'matches', views.MatchViewset, basename='Match')

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path('authenticate/', views.CustomObtainAuthToken.as_view())

]