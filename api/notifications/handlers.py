import logging
import datetime
from api.notifications.models import UserNotificantion
from base import ApiHandler, die
from helpers import route
from utility.average_response_time import calculate_average_response_time
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/new_notifications')
class NewNotificationsHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        # get all new notifications
        return self.success({
            'count': self.user.user_notifications.filter(UserNotificantion.seen_at == None).count()
        })


@route('user/notifications')
class NotificationsHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        # get all notifications
        notifications = self.user.user_notifications

        need_calculation = False

        # go through every notification, add seen_at time and duration time
        for n in notifications:
            if not n.seen_at:
                need_calculation = True
                n.seen_at = datetime.datetime.utcnow()
                n.response_time = (n.seen_at - n.created_at).total_seconds()

        if need_calculation:
            # calculate average response time
            self.user.average_response_time = calculate_average_response_time(self.user)
            self.session.commit()

        # get all new notifications
        return self.success({
            'notifications': [n.response for n in self.user.user_notifications]
        })