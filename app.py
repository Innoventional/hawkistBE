import os
from tornado import web
from environment import env
from helpers import make_handlers, include


ROOT = os.path.abspath(os.path.dirname(__file__))


class HawkistApi(web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None,
                 wsgi=False, **settings):
        super(HawkistApi, self).__init__(self.get_handlers(), **{
            'cookie_secret': env['cookie_secret'],
            'debug': env['debug'],
            'template_path': 'templates',
            'static_path': os.path.join(ROOT, 'static'),
            'static_url_prefix': env['static_url'],
        })

    def get_handlers(self):
        res = make_handlers(env.get('url_prefix', ''),
            (r'/(robots\.txt|favicon\.ico)', web.StaticFileHandler, {"path": os.path.join(ROOT, 'static')}),
            (r'/api/', include('api.handlers')),
            (r'/static/(.*)', web.StaticFileHandler, {'path': os.path.join(ROOT, 'static')}),
            (r'', include('handlers')),
        )
        if env.get('serve_static'):
            res += make_handlers(env.get('url_prefix', ''),
                                 (r'/s/(.*)', web.StaticFileHandler, {"path": os.path.join(ROOT, 'static')}),
            )
        return res