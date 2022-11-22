import re

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
            serializer = self.get_serializer(politician)
            first_letter = ''

            if serializer.data['screen_name']:
                first_letter = serializer.data['screen_name'][0].upper()

            # Si esta vacio el screen_name o si no es una letra (osea un caracter raro como @  . y otros)
            if not re.search('[a-zA-Z]', first_letter) or not serializer.data['screen_name']:
                # Busco la primer letra del user_name, evitando caracteres especiales
                first_letter = re.findall('[a-zA-Z]', serializer.data['user_name'])[0].upper()

            try:
                results[first_letter].append(serializer.data)
            except:
                results[first_letter] = []
                results[first_letter].append(serializer.data)

        # Ordeno alfabeticamente
        results = {k: results[k] for k in sorted(results)}

        return Response(results)
