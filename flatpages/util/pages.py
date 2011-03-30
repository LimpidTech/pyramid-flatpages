import os

# Temporarily, we will import git directly for testing.
from ..data_sources.git import GitDataSource

def render(request, info=None):
    """ A util that we use to centralize rendering of flatpages. """

    if hasattr(request, 'subpath'):
        lookup_string = os.sep.join(request.subpath)
    else:
        if info:
            lookup_string = os.sep.join(info['match']['subpath'])

    if hasattr(request, 'view_name') and len(request.view_name) > 0:
        lookup_string = os.sep.join(request.view_name, request.subpath)

    if lookup_string[-1] == os.sep:
        lookup_string = lookup_string[:-1]

    g = GitDataSource()
    file_contents = g.read(lookup_string)

    # If file_info is None, this file doesn't exist. So, a 404 is the proper
    # response in this situation.
    if file_contents is None:
        return False

    request.flatpage_contents = file_contents
    return True
