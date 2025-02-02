from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

class DataTablePagination(PageNumberPagination):
    """
    Pagination class compatible with jQuery DataTables.
    
    Expected query parameters:
    - length: Number of records to return (page_size)
    - start: Starting index of records (page_size * (page - 1))
    - draw: Draw counter for DataTables
    - order[column]: Column index to sort by
    - order[dir]: Sort direction (asc/desc)
    """
    page_size_query_param = 'length'
    page_size = 10
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return response in DataTables expected format."""
        return Response(OrderedDict([
            ('draw', int(self.request.query_params.get('draw', 1))),
            ('recordsTotal', self.page.paginator.count),
            ('recordsFiltered', self.page.paginator.count),
            ('data', data)
        ]))

    def get_page_size(self, request):
        """Get the page size from the 'length' parameter or use default."""
        if self.page_size_query_param:
            try:
                return int(request.query_params[self.page_size_query_param])
            except (KeyError, ValueError):
                pass
        return self.page_size
    
    def get_page_number(self, request, paginator):
        """
        Calculate page number from DataTables 'start' parameter.
        
        Args:
            request: The request object
            paginator: The paginator instance
        Returns:
            The page number
        """
        try:
            start = int(request.query_params.get('start', 0))
            page_size = self.get_page_size(request)
            if page_size:
                return (start // page_size) + 1
        except ValueError:
            pass
        return 1 