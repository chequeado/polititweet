from rest_framework.generics import ListAPIView
from rest_framework import filters
from rest_framework.response import Response

from tracker.models import User
from api import serializers


class UsersView(ListAPIView):
    '''Viewset listing targeted users.'''
    serializer_class = serializers.UserSerializer
    queryset = User.objects.filter(monitored=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_data__name', 'full_data__screen_name']
    ordering_fields = ['full_data__name', 'full_data__screen_name']
    ordering = ['full_data__name']

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        results = {}
        for politician in queryset:
            first_letter = politician.screen_name[0].upper()
            serializer = self.get_serializer(politician)

            try:
                results[first_letter].append(serializer.data)
            except:
                results[first_letter] = []
                results[first_letter].append(serializer.data)

        return Response(results)
