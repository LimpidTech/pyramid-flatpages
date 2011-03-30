from .util.pages import render

class FlatPagesPredicate(object):
    """ This is a predicate which allows us to only serve up files that actually
    exist within our data sources through a catch-all route. """

    package = None
    subdir = None

    def __call__(self, info, request):
        """ Calls our render method (which attacks flatfile_contents to the
        request) and returns True or False depending on whether this specific
        file was found in our data store.

        """

        output = render(request, info)
        return output
