from pyramid.response import Response
from pyramid.view import view_config
from pyramid.exceptions import NotFound

from .interfaces import IFlatPagesRoot
from .util.pages import render

def handle_flatpage(request):
    if not hasattr(request, 'flatpage_contents'):
        result = render(request)

        if result is False:
            raise NotFound

    return Response(request.flatpage_contents)
