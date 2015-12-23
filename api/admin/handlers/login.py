import logging
from api.users.models import User, UserType
from base import HttpRedirect, OpenApiHandler
from environment import env
from helpers import route, encrypt_password
from ui_messages.errors.admin_errors.admin_login_errors import ADMIN_LOGIN_USER_NOT_FOUND, \
    ADMIN_LOGIN_USER_WRONG_PASSWORD, ADMIN_LOGIN_USER_ACCESS_DENIED

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('test_jwt_token')
class TestJWTHandler(OpenApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        from utility.zendesk_api import zendesk_create_jwt

        return zendesk_create_jwt(140, 'Sergey_Borichev', 'gigek@mail.ru')


class AdminBaseHandler(OpenApiHandler):
    pass

@route('admin')
class AdminHandler(AdminBaseHandler):
    allowed_methods = ('GET', )

    def read(self):
        return HttpRedirect('/api/admin/login')


@route('admin/login')
class AdminLoginHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):
        if self.user:
            return HttpRedirect('/api/admin/users')

        return self.render_string('admin/admin_login.html', undefined_user=True, menu_tab_active='')

    def create(self):

        email = self.get_argument('email').lower()
        password = self.get_argument('password')
        message = None

        logger.debug("USER_LOGIN. Email {0}, password {1}".format(email, password))

        # because we store encrypted passwords (not entered user text) before user password compare we encrypted
        # password which get from request parameters
        encrypted_pass = encrypt_password(password, env['password_salt'])
        user = self.session.query(User).filter(User.email == email).first()

        if not user:
            message = ADMIN_LOGIN_USER_NOT_FOUND % email

        # elif user.password != encrypted_pass:
        #     message = ADMIN_LOGIN_USER_WRONG_PASSWORD

        elif user.user_type == UserType.Standard:
            message = ADMIN_LOGIN_USER_ACCESS_DENIED

        if message:
            return self.render_string('admin/admin_login.html', message=message, menu_tab_active='',
                                      undefined_user=True)

        self.user = user
        return HttpRedirect('/api/admin/users')


@route('admin/logout')
class AdminLogoutHandler(AdminBaseHandler):
    allowed_methods = ('GET', )

    def read(self):
        logger.debug('USER_LOGOUT.')
        if self.user:
            logger.debug(self.user)
            self.user = None

        return HttpRedirect('/api/admin/login')
