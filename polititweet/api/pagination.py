from rest_framework import pagination

class StandardPagination(pagination.PageNumberPagination):
    page_size = 20 # Cantidad de resultados a devolver por página
    page_size_query_param = 'page_size' # Parámetro para cambiar la cantidad de resultados a devolver por página
    max_page_size = 100  # Cantidad máxima de resultados a devolver por página