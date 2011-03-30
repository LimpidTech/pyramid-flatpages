from pyramid.response import Response
from pyramid.view import view_config

from .resources import Resource

@view_config(request_method='GET', context=Resource)
def hello_world(request):
    return Response('Hello, world.')