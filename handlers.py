from base import ApiHandler
from helpers import route


@route('')
class IndexHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        return {
            'welcome_message': 'Hello!'
        }
