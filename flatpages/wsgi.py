from pyramid.config import Configurator

from .routes import FlatPagesPredicate
from .extensibility import include_me
from .resources import Resource
from .views import handle_flatpage

renderers = {
    'flatpages.renderers.markdown.MarkdownRendererFactory': [
        'md',
        'markdown'
    ],
}

def factory(global_config, **settings):
    """ Application entry point factory for serving with wsgi.

    The application entry point. Provides a WSGI application that represents
    our a basic pyramid application which uses Vaktuk. Usually, you will want to
    create your own application and do something akin to what this function does
    in order to use the CMS - but also extend it with your own functionality.

    """

    config = Configurator(settings=settings, root_factory=Resource.factory)

    config.include(include_me)

    # Adds each file extension as a renderer based on the renderers dict
    for renderer in renderers:
        for extension in renderers[renderer]:
            config.add_renderer('.{0}'.format(extension), factory=renderer)

    config.add_route('', '*subpath', handle_flatpage,
                     custom_predicates=[FlatPagesPredicate()])

    return config.make_wsgi_app()
