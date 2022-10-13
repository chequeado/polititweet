
from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import viewsets


router = DefaultRouter()
router.register('deleted-tweets', viewsets.DeletedTweetsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
