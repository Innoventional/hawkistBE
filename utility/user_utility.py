import datetime

__author__ = 'ne_luboff'


# after every user action we must update user last activity time
def update_user_last_activity(self):
    self.user.last_activity = datetime.datetime.utcnow()
    self.session.commit()
