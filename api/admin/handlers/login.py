from api.admin.handlers.tags import AdminBaseHandler
from api.users.models import User, UserType
from base import HttpRedirect
from environment import env
from helpers import route, encrypt_password

__author__ = 'ne_luboff'


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

        # because we store encrypted passwords (not entered user text) before user password compare we encrypted
        # password which get from request parameters
        encrypted_pass = encrypt_password(password, env['password_salt'])
        user = self.session.query(User).filter(User.email == email).first()

        if not user:
            message = 'No user with email %s' % email

        elif user.password != encrypted_pass:
            message = 'Wrong password'

        elif user.user_type == UserType.Standard:
            message = 'Access denied. Your user type - standard user'

        if message:
            return self.render_string('admin/admin_login.html', message=message, menu_tab_active='',
                                      undefined_user=True)

        self.user = user
        return HttpRedirect('/api/admin/users')


@route('admin/logout')
class AdminLogoutHandler(AdminBaseHandler):
    allowed_methods = ('GET', )

    def read(self):
        if self.user:
            self.user = None

        return HttpRedirect('/api/admin/login')
