from .routes import FlatPagesPredicate
from .views import handle_flatpage
from .renderers.defaults import renderers as default_renderers

def flatpages_root(config, insert_renderers=True, root_path=''):

    # Adds each file extension as a renderer based on the renderers dict
    if insert_renderers is True:
        for renderer in default_renderers:
            for extension in default_renderers[renderer]:
                config.add_renderer('.{0}'.format(extension), factory=renderer)

    config.add_route('', '*subpath', handle_flatpage,
                     custom_predicates=[FlatPagesPredicate()])

def include_me(config, module_name='flatpages'):
    """ Extensibility function for embedding the CMS in other Pyramid apps.

    Pyramid will use this function on another application's configuration when
    this module is loaded through a call to 'include' on Configurator instances
    with the vaktuk module given as an argument.

    """

    config.scan(module_name)
