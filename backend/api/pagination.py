"""Pagination module for REST framework."""

from rest_framework.pagination import PageNumberPagination

from api.constants import DEFAULT_PAGE_SIZE_QUERY_PARAM, MAX_PAGE_SIZE


class PageNumberPagination(PageNumberPagination):
    """Pagination class with configurable page size."""

    page_size_query_param = DEFAULT_PAGE_SIZE_QUERY_PARAM
    max_page_size = MAX_PAGE_SIZE
