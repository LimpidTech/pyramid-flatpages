from pyramid.config import Configurator

from .extensibility import include_me, flatpages_root
from .resources import Resource

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

    flatpages_root(config)

    return config.make_wsgi_app()
