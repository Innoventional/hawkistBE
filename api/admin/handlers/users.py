from random import choice
import string
from api.admin.handlers.tags import AdminBaseHandler
from api.users.models import User, SystemStatus, UserType
from base import paginate, HttpRedirect
from environment import env
from helpers import route, encrypt_password
from utility.send_email import send_email

__author__ = 'ne_luboff'


@route('admin/users')
class AdminUsersHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        users = self.session.query(User).order_by(User.id)

        page = self.get_arg('p', int, 1)
        page_size = self.get_arg('page_size', int, 100)

        paginator, tags = paginate(users, page, page_size)

        return self.render_string('admin/admin_users.html', users=users, paginator=paginator,
                                  menu_tab_active='tab_users', SystemStatus=SystemStatus, UserType=UserType)

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        user_id = self.get_arg('user_id')
        new_user_type = int(self.get_arg('user_type_id'))
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return self.make_error('Something wrong. Try again later')

        if not user.email:
            return self.make_error("Forbidden action.\nThis user has no email address in profile")

        if not user.email_status:
            return self.make_error("Forbidden action.\nThis user didn't confirm his email address yet")

        if user.user_type != new_user_type:
            text = ''
            if new_user_type == 0:
                text = 'Looks like you were excluded from Hawkist %s user group.' % UserType.tostring(user.user_type)
            else:
                # generate password
                chars = string.ascii_letters
                password = ''.join(choice(chars) for _ in xrange(8))
                number_count = choice([i for i in range(1, 4)])
                while number_count != 0:
                    gap_position = choice([i for i in xrange(8)])
                    number = choice([i for i in xrange(10)])
                    password = password[:gap_position] + str(number) + password[gap_position:]
                    number_count -= 1

                encrypted_pass = encrypt_password(password=password, salt=env['password_salt'])
                user.password = encrypted_pass
                # send email with pass
                text = 'Congrats!\nYou were added to Hawkist %s user group. Go to %s  and use your email address and ' \
                       'this temporary password to log in administration tool:\n%s\nEnjoy!' % \
                       (UserType.tostring(new_user_type), env['server_address'] + '/api/admin/login', password)
            user.user_type = new_user_type
            self.session.commit()
            subject = 'Permissions changed'
            send_email(text, subject=subject, recipient=user.email)
        return self.success()

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        user_id = self.get_arg('user_id')
        action = self.get_arg('action')

        new_system_status = 0

        if action == 'suspend':
            new_system_status = 1
        elif action == 'unsuspend':
            new_system_status = 0

        # get user to be changed
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return self.make_error('Something wrong. Try again later')
        user.system_status = new_system_status
        self.session.commit()
        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        user_id = self.get_arg('user_id')
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return self.make_error('Something wrong. Try again later')
        self.session.delete(user)
        self.session.commit()
        return self.success()
