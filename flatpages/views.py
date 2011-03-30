from pyramid.response import Response
from pyramid.view import view_config
from pyramid.exceptions import NotFound
import os

from .interfaces import IFlatPagesRoot

# Temporarily, we will import git directly for testing.
from .data_sources.git import GitDataSource

def handle_flatpage(request):
    lookup_string = os.sep.join(request.subpath)

    if len(request.view_name) > 0:
        lookup_string = os.sep.join(request.view_name, request.subpath)

    if lookup_string[-1] == os.sep:
        lookup_string = lookup_string[:-1]

    g = GitDataSource()
    file_contents = g.read(lookup_string)

    print 'Looking for: {0}'.format(lookup_string)

    # If file_info is None, this file doesn't exist. So, a 404 is the proper
    # response in this situation.
    if file_contents is None:
        raise NotFound

    return Response(file_contents)
