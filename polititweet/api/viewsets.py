from rest_framework import (
    viewsets,
    mixins,
    status,
)

from tracker.models import (
    Tweet,
    User,
)
from api import serializers


class DeletedTweetsViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset listing deleted tweets.'''
    serializer_class = serializers.DeletedTweetSerializer
    queryset = Tweet.objects.filter(deleted=True).order_by('-deleted_time')
