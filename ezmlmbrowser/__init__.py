from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('lists', '/')
    config.add_static_view('static/favicon.ico', '/favicon.ico')
    config.add_route('list', '/{list}/')
    config.add_route('thread', '/{list}/t/{thread}')
    config.add_route('author', '/{list}/a/{author}')
    config.add_route('threads', '/{list}/d/{year}/{month}')
    config.add_route('message', '/{list}/m/{messageid}')
    config.scan()
    return config.make_wsgi_app()
