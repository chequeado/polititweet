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
    search_fields = ['full_text', 'full_data__user__name', 'full_data__user__screen_name']

class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset listing targeted users.'''
    serializer_class = serializers.UserSerializer
    queryset = User.objects.filter(monitored=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_data__name', 'full_data__screen_name']
    ordering_fields = ['full_data__name', 'full_data__screen_name']
    ordering = ['full_data__name']
