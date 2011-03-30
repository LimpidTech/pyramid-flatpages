from __future__ import absolute_import # Since 2.x sucks! :)

from pyramid.response import Response
import markdown

from ..data_sources.shortcuts import get_data_source

class MarkdownRendererFactory(object):
    def __init__(self, info=None):
        if info:
            for key in ['name', 'package', 'type', 'registry', 'settings']:
                if hasattr(info, key):
                    setattr(self, key, getattr(info, key))

    def __call__(self, value, system):
        file_contents = getattr(system['request'], 'flatpage_contents', False)

        if file_contents:
            result = markdown.markdown(file_contents)
        else:
            # TODO: Implement the real deal.
            pass

        return result
