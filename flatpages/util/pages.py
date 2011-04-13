from pyramid import renderers
import os

from ..data_sources.shortcuts import get_data_source

def render(request, info=None):
    """ A util that we use to centralize rendering of flatpages. """

    if hasattr(request, 'subpath'):
        lookup_string = os.sep.join(request.subpath)
    else:
        if info:
            lookup_string = os.sep.join(info['match']['subpath'])

    if hasattr(request, 'view_name') and len(request.view_name) > 0:
        lookup_string = os.sep.join(request.view_name, request.subpath)

    if len(lookup_string) > 0 and lookup_string[-1] == os.sep:
        lookup_string = lookup_string[:-1]

    g = get_data_source(request)
    file_info = g.read(lookup_string)

    # If file_info is None, this file doesn't exist. So, a 404 is the proper
    # response in this situation.
    if file_info is None:
        return False

    # Some metadata about this page is added to the request
    request.flatpage_contents = file_info[0]
    request.flatpage_filename = file_info[1]

    # Attempt to hook into our view renderer for some additiona functionality
    rendered_content = renderers.render(file_info[1], {}, request)

    if rendered_content:
        request.flatpage_contents = rendered_content

    return True
