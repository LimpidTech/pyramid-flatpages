# Temporarily, we will import git directly for testing.
from ..data_sources.git import GitDataSource

def get_data_source(request):
    """ Returns the data source to be used with the given request. """

    return GitDataSource()
