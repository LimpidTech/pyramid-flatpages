def include_me(config, module_name='flatpages'):
    """ Extensibility function for embedding the CMS in other Pyramid apps.

    Pyramid will use this function on another application's configuration when
    this module is loaded through a call to 'include' on Configurator instances
    with the vaktuk module given as an argument.

    """

    config.scan(module_name)
