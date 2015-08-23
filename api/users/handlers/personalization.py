import logging
from base import ApiHandler, die
from helpers import route
from utility.user_utility import check_user_suspension_status, update_user_last_activity

__author__ = 'ne_luboff'


logger = logging.getLogger(__name__)


@route('user/holiday_mode')
class UserHolidayModeHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        return self.success({'holiday_mode': self.user.holiday_mode})

    def update(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_USER_HOLIDAY_MODE')
        logger.debug(self.request_object)

        holiday_mode = ''

        if self.request_object:
            if 'holiday_mode' in self.request_object:
                holiday_mode = self.request_object['holiday_mode']

        if self.user.holiday_mode != holiday_mode:
            if holiday_mode:
                self.user.holiday_mode = True
            else:
                self.user.holiday_mode = False
            self.session.commit()

        return self.success({'holiday_mode': self.user.holiday_mode})


@route('user/notify_about_favorite')
class UserNotifyAboutFavoriteHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        return self.success({'notify_about_favorite': self.user.notify_about_favorite})

    def update(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_USER_NOTIFY_ABOUT_FAVORITE')
        logger.debug(self.request_object)

        notify_about_favorite = ''

        if self.request_object:
            if 'notify_about_favorite' in self.request_object:
                notify_about_favorite = self.request_object['notify_about_favorite']

        if self.user.notify_about_favorite != notify_about_favorite:
            if notify_about_favorite:
                self.user.notify_about_favorite = True
            else:
                self.user.notify_about_favorite = False
            self.session.commit()

        return self.success({'notify_about_favorite': self.user.notify_about_favorite})
