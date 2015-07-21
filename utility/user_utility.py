import datetime
from api.users.models import SystemStatus
from ui_messages.messages.custom_error_titles import USER_SUSPENDED_TITLE
from ui_messages.messages.user_messages import USER_SUSPENDED

__author__ = 'ne_luboff'


# after every user action we must update user last activity time
def update_user_last_activity(self):
    self.user.last_activity = datetime.datetime.utcnow()
    self.session.commit()


def check_user_suspension_status(user):
    if user.system_status == SystemStatus.Suspended:
        return {'status': 403,
                'message': USER_SUSPENDED,
                'title': USER_SUSPENDED_TITLE}
    return False
