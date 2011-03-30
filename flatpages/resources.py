from zope.interface import implements
from .interfaces import IFlatPagesRoot

class Resource(object):
    """ A very generic example resource that implements our flatpages interface,
    so that it can be used as a root for serving flatpages. """

    implements(IFlatPagesRoot)

    __parent__ = None
    __name__ = None

    def __init__(self, request, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        self.request = request

    def __getitem__(self, name):
        raise KeyError('Finished iterating tree for traversal.')

    @classmethod
    def factory(cls, *args, **kwargs):
        return cls(*args, **kwargs)
