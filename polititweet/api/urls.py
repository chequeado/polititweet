
from django.conf.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from . import viewsets, views


router = SimpleRouter()
router.register('deleted-tweets', viewsets.DeletedTweetsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('politicians/', views.UsersView.as_view(), name='politicians')
]
