from random import choice
import string
import datetime
from sqlalchemy import and_, func
from api.admin.handlers.tags import AdminBaseHandler
from api.users.models import User, SystemStatus, UserType
from base import paginate, HttpRedirect
from environment import env
from helpers import route, encrypt_password
from utility.format_verification import username_verification, email_verification, phone_verification
from utility.send_email import send_email, email_confirmation_sending
from utility.twilio_api import send_sms

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
                                  menu_tab_active='tab_users', SystemStatus=SystemStatus, UserType=UserType,
                                  current_user=self.user)

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
        return self.success({'message': 'User has been added to %s user group' % UserType.tostring(new_user_type)})

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        user_id = self.get_arg('user_id')
        action = self.get_arg('action')

        # get user to be changed
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return self.make_error('Something wrong. Try again later')

        if action == 'suspend':
            user.system_status = 1
        elif action == 'unsuspend':
            user.system_status = 0
        elif action == 'edit':
            username = self.get_arg('username')
            email = self.get_arg('email')
            phone = self.get_arg('phone')

            # step-by-step
            # username
            if user.username != username and username:
                username = str(username.encode('utf-8'))
                username_error = username_verification(username)
                if username_error:
                    return self.make_error(username_error)

                already_used = self.session.query(User).filter(and_(User.id != user.id,
                                                                    func.lower(User.username) == username.lower())).first()
                if already_used:
                    return self.make_error("Sorry, username '%s' already used by another user" % username)
                user.username = username

            # email
            if user.email != email and email:
                email = str(email.encode('utf-8')).lower()
                # first validate email
                email_error = email_verification(email)
                if email_error:
                    return self.make_error(email_error)

                already_used = self.session.query(User).filter(and_(User.id != user.id,
                                                                    User.email == email)).first()
                if already_used:
                    return self.make_error("Sorry, email address '%s' already used by another user" % email)

                user.email = email

                user.email_status = False
                # send email confirmation
                email_confirmation_sending(self, self.user, email)

            # phone
            if user.phone != phone and phone:
                phone = str(phone)
                phone = phone.replace('+', '')
                # first verify number
                phone_error = phone_verification(phone)
                if phone_error:
                    return self.make_error(phone_error)

                already_used = self.session.query(User).filter(and_(User.id != user.id,
                                                                    User.phone == phone)).first()
                if already_used:
                    return self.make_error("Sorry, phone number '%s' already used by another user" % phone)

                # send message to email
                if user.email:
                    text = 'Hi!\nYour phone number has changed. New login pin sent to new number.\nEnjoy!'
                    subject = 'Phone number changed'
                    send_email(text, subject=subject, recipient=user.email)

                # generate pin code
                confirm_code = ''.join(choice(string.digits) for _ in xrange(4))
                message_body = 'Hi! Your phone number has changed! Use this code to login:\n%s' % confirm_code

                # and send it to user
                error = send_sms(phone, message_body)
                if error:
                    return {'status': 2,
                            'message': error}
                user.phone = phone
                user.pin = confirm_code
                user.last_pin_sending = datetime.datetime.utcnow()
                if user.sent_pins_count:
                    user.sent_pins_count += 1
                else:
                    user.sent_pins_count = 0

        user.updated_at = datetime.datetime.utcnow()
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
