from StringIO import StringIO

import base64
import json
import logging
import threading
import math
from tornado.websocket import WebSocketHandler
from types import GeneratorType
import sys
from tornado import web, ioloop
import zlib
from api.users.models import User
from environment import env
from helpers import ApiJsonEncoder, parse_datetime, parse_int, UrlOpener
from api.models import ApiKey
from orm import Base, create_session
import csv


logger = logging.getLogger(__name__)
USER_ID = 'user-id'

def die(code):
    raise web.HTTPError(code)


def json_encode(v):
    return json.dumps(v, cls=ApiJsonEncoder, indent=4 if env['debug'] else None) if v is not None else ''


class HttpRedirect(object):
    def __init__(self, url):
        self.url = url


def redirect(url):
    return HttpRedirect(url)


class ThreadableRequestHandler(web.RequestHandler):
    def start_worker(self, *args, **kwargs):
        worker_method = self._worker
        threading.Thread(target=worker_method, args=args, kwargs=kwargs).start()

    def worker(self, *args, **kwargs):
        raise web.HTTPError(501)

    def _worker(self, *args, **kwargs):
        res = None
        try:
            res = self.worker(*args, **kwargs)
        except web.HTTPError, e:
            self.set_status(e.status_code)
        except Exception, e:
            self.exc_info = sys.exc_info()
            logger.error(e.message, exc_info=True)
            self.set_status(500)
        ioloop.IOLoop.instance().add_callback(self.async_callback(self.results, res))

    def results(self, res):
        if isinstance(res, HttpRedirect):
            self.redirect(res.url)
        elif self.get_status() >= 400:
            kw = {}
            if hasattr(self, 'exc_info'):
                kw['exc_info'] = self.exc_info
            self.write_error(self.get_status(), **kw)
        else:
            accept_header = self.request.headers.get('Accept') or ''
            if 'csv' in accept_header:
                self.set_header("Content-Type", "text/csv")
                if isinstance(res, (list, tuple)) and res:
                    csvfile = StringIO()
                    writer = csv.writer(csvfile)
                    if isinstance(res[0], dict):
                        for r in res:
                            writer.writerow(r.values())
                    elif isinstance(res[0], (list, tuple)):
                        for r in res:
                            writer.writerow(r)
                    self.finish(csvfile.getvalue())
                else:
                    self.finish()
            else:
                # return JSON
                if isinstance(res, GeneratorType):
                    res = list(res)

                if isinstance(res, (dict, list, tuple, Base)):
                    self.set_header("Content-Type", "application/json; charset=UTF-8")
                    res = json_encode(res)
                self.finish(res)

    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = create_session(lambda: self.request)
        return self._session

    def on_finish(self):
        if hasattr(self, '_session'):
            self._session.remove()


class BaseRequestHandler(ThreadableRequestHandler):
    _ARG_DEFAULT = 'dd3f4da1-4bba-4b22-a3bd-963c74493a44'
    def get_arg(self, name, func=None, default=_ARG_DEFAULT):
        if default == self._ARG_DEFAULT:
            default = {
                int: 0,
                str: '',
                }.get(func)
        if func:
            def the_func(x):
                try:
                    return func(x)
                except Exception:
                    return default
        else:
            the_func = lambda x: x
        v = map(the_func, self.get_arguments(name)) or [default]
        return v[0] if len(v) == 1 else v

    def get_arg_datetime(self, name, default=_ARG_DEFAULT):
        return self.get_arg(name, parse_datetime, default)

    def get_arg_int(self, name, default=_ARG_DEFAULT):
        return self.get_arg(name, parse_int, default)

    @property
    def request_object(self):
        if not hasattr(self, '_request_object'):
            b = self.request.body
            if self.request.headers.get('Content-Encoding') == 'gzip':
                b = zlib.decompress(b)
            try:
                self._request_object = json.loads(b)
            except:
                self._request_object = None

        return self._request_object

    @property
    def url_opener(self):
        if not hasattr(self, '_url_opener'):
            self._url_opener = UrlOpener()
        return self._url_opener


class ApiHandler(BaseRequestHandler):
    allowed_methods = ()

    @staticmethod
    def make_error(message=None, status=1, title='Error'):

        response = {
            'status': status,
            'title': title
        }

        if message:
            response['message'] = message

        logger.debug('Error: {0}'.format(response))
        return response

    @staticmethod
    def success(data=None):
        response = {
            'status': 0,
        }

        if data is not None:
            response.update(data)

        logger.debug('Success: {0}'.format(response))
        return response

    def test_auth(self, api_key, api_pass):
        try:
            return self.session.query(ApiKey).filter_by(api_key=api_key, api_pass=api_pass).one()
        except Exception, e:
            return None

    def get_user(self):

        if hasattr(self, '_user'):
            return getattr(self, '_user')

        u = None
        user_id = self.get_secure_cookie(USER_ID)

        if user_id is not None:
            u = self.session.query(User).get(user_id)
            setattr(self, '_user', u)

        return u

    def set_user(self, user):
        if user is None:
            self.clear_cookie(USER_ID)
        else:
            self.set_secure_cookie(USER_ID, str(user.id), expires_days=30)
        setattr(self, '_user', user)

    user = property(fget=get_user, fset=set_user)

    def test_session(self):
        try:
            auth_type, auth_token = self.request.headers.get('Authorization').split()
            if auth_type != 'Basic':
                return False
            api_key, api_pass = base64.decodestring(auth_token).split(':')
            
            # if its our key-pass - don't show
            authorization_credentials = self.session.query(ApiKey).filter_by(api_key=api_key, api_pass=api_pass).one()
            if api_key != authorization_credentials.api_key or api_pass != authorization_credentials.api_pass:
                logger.debug('It looks like someone wants to break us')
                logger.debug('api_key, api_pass = %s, %s', api_key, api_pass)

            self.ApiKey = self.test_auth(api_key, api_pass)
            return self.ApiKey is not None
        except Exception:
            return False

    def _worker(self, method, *args, **kwargs):
        res = None
        try:
            if not self.test_session():
                self.set_header('WWW-Authenticate', 'Basic realm="You shall not pass"')
                self.set_status(401)
            elif method not in self.allowed_methods:
                self.set_status(405)
            else:
                m = {
                    'GET': 'read',
                    'POST': 'create',
                    'PUT': 'update',
                    'DELETE': 'remove',
                    }[method]
                w = getattr(self, m, self.worker)
                res = w(*args, **kwargs)
        except web.HTTPError, e:
            self.set_status(e.status_code)
        except Exception, e:
            self.exc_info = sys.exc_info()
            logger.error(e.message, exc_info=True)
            self.set_status(500)
        ioloop.IOLoop.instance().add_callback(self.async_callback(self.results, res))

    @web.asynchronous
    def get(self, *args, **kwargs):
        self.start_worker('GET', *args, **kwargs)

    @web.asynchronous
    def post(self, *args, **kwargs):
        self.start_worker('POST', *args, **kwargs)

    @web.asynchronous
    def put(self, *args, **kwargs):
        self.start_worker('PUT', *args, **kwargs)

    @web.asynchronous
    def push(self, *args, **kwargs):
        self.start_worker('PUSH', *args, **kwargs)

    @web.asynchronous
    def delete(self, *args, **kwargs):
        self.start_worker('DELETE', *args, **kwargs)


class OpenApiHandler(ApiHandler):
    def test_session(self):
        return True


def paginate(qs, page, page_size):
    count = qs.count()
    if page_size > 0:
        pages = int(math.ceil(float(count) / page_size))
    else:
        pages = 1

    page = max(page, 1)
    page = min(page, pages)

    if page_size > 0:
        qs = qs.limit(page_size)
        if pages:
            qs = qs.offset(page_size*(page-1))

    return {
        'page': page,
        'pages': pages,
        'items_count': count,
    }, qs


class BaseWebSocketHandler(WebSocketHandler):
    session = None
    # @property
    # def session(self):
    #     if not hasattr(self, '_session'):
    #         self._session = create_session(lambda: self.request)
    #     return self._session

    # def on_close(self):
    #     logger.debug('Remove orm session. On close.')
        # if hasattr(self, '_session'):
        #     self._session.remove()

    def on_connection_close(self):
        logger.debug('Remove orm session. On connection close:')
        # logger.debug(self.user.id)
        # if hasattr(self, '_session'):
        #     self._session.remove()

    def get_user(self):

        if hasattr(self, '_user'):
            return getattr(self, '_user')

        u = None
        user_id = self.get_secure_cookie(USER_ID)

        if user_id is not None:
            u = self.session.query(User).get(user_id)
            setattr(self, '_user', u)

        return u

    def set_user(self, user):
        if user is None:
            self.clear_cookie(USER_ID)
        else:
            self.set_secure_cookie(USER_ID, str(user.id), expires_days=30)
        setattr(self, '_user', user)

    user = property(fget=get_user, fset=set_user)
