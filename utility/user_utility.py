import datetime
from api.users.models import SystemStatus, User
from ui_messages.errors.users_errors.update_errors import UPDATE_USER_INFO_EMAIL_ALREADY_USED
from ui_messages.messages.custom_error_titles import USER_SUSPENDED_TITLE
from ui_messages.messages.user_messages import USER_SUSPENDED

__author__ = 'ne_luboff'


def check_email_uniqueness(self, email):
    user = self.session.query(User).filter(User.email == email).first()
    if user:
        return UPDATE_USER_INFO_EMAIL_ALREADY_USED % email
    return False


# after every user action we must update user last activity time
def update_user_last_activity(self):
    self.user.last_activity = datetime.datetime.utcnow()
    self.session.commit()


def check_user_suspension_status(user):
    if user.system_status == SystemStatus.Suspended:
        return {
            'status': 403,
            'message': USER_SUSPENDED,
            'title': USER_SUSPENDED_TITLE
        }
    return False
