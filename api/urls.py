from django.urls import re_path

from api import views
from rest_framework import routers
from django.conf.urls import include

router = routers.DefaultRouter()
router.register(r'players', views.PlayerViewset)

urlpatterns = [
    re_path(r'^', include(router.urls)),
]