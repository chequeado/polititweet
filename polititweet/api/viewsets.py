from rest_framework import (
    viewsets,
    filters,
)

from tracker.models import Tweet
from api import serializers
from api.pagination import StandardPagination


class DeletedTweetsViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset listing deleted tweets.'''
    serializer_class = serializers.DeletedTweetSerializer
    queryset = Tweet.objects.filter(deleted=True).order_by('-deleted_time')
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_text', 'full_data__user__name', 'full_data__user__screen_name']
