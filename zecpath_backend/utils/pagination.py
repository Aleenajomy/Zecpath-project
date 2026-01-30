from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response
from django.conf import settings

class StandardPageNumberPagination(PageNumberPagination):
    """Offset-based pagination with complete metadata"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.get_page_size(self.request),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

class JobCursorPagination(CursorPagination):
    """Cursor-based pagination for real-time data"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
class ApplicationCursorPagination(CursorPagination):
    """Cursor-based pagination for applications"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    ordering = '-applied_at'
    cursor_query_param = 'cursor'