"""Custom pagination module for REST framework."""

from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class with configurable page size."""

    page_size_query_param = 'limit'
    max_page_size = 6
