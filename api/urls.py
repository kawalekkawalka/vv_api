from django.urls import re_path

from api import views
from rest_framework import routers
from django.conf.urls import include

router = routers.DefaultRouter()
router.register(r'players', views.PlayerViewset)
router.register(r'teams', views.TeamViewset)

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path('authenticate/', views.CustomObtainAuthToken.as_view())
]