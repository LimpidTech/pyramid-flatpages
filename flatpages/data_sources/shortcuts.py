# Temporarily, we will import git directly for testing.
from ..data_sources.git import GitDataSource

def get_data_source(request):
    return GitDataSource()
