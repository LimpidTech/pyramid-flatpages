from pyramid.response import Response
from pyramid.view import view_config

from .interfaces import IFlatPagesRoot

@view_config(request_method='GET', context=IFlatPagesRoot)
def hello_world(request):
    return Response('Hello, world.')
