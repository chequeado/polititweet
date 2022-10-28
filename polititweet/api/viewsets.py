from rest_framework import (
    viewsets,
    mixins,
    status,
    filters,
)

from tracker.models import (
    Tweet,
    User,
)
from api import serializers
from api.pagination import StandardPagination


class DeletedTweetsViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset listing deleted tweets.'''
    serializer_class = serializers.DeletedTweetSerializer
    queryset = Tweet.objects.filter(deleted=True).order_by('-deleted_time')
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__screen_name', 'user__user_name', 'full_text']

class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset listing targeted users.'''
    serializer_class = serializers.UserSerializer
    queryset = User.objects.filter(monitored=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['screen_name', 'user_name']
    ordering_fields = ['screen_name', 'user_name']
    ordering = ['-screen_name']
