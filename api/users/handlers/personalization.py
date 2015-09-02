import json
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


@route('user/push_notifications')
class UserEnablePushNotificationsHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        return self.success(self.user.push_response)

    def update(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_USER_AVAILABLE_PUSH_NOTIFICATIONS')
        logger.debug(self.request_object)

        enable = ''
        type = ''

        if self.request_object:
            if 'enable' in self.request_object:
                enable = self.request_object['enable']

            if 'type' in self.request_object:
                type = str(self.request_object['type'])

        need_commit = False
        if len(str(enable)) != 0:
            if self.user.available_push_notifications != enable:
                if enable:
                    self.user.available_push_notifications = True
                else:
                    self.user.available_push_notifications = False
                need_commit = True

        if len(type) != 0:
            current_user_push_types = json.loads(json.loads(json.dumps(self.user.available_push_notifications_types))) \
                if self.user.available_push_notifications_types else '{}'
            try:
                # get current type status
                current_type_status = current_user_push_types.get(type)
                # change status
                if current_type_status:
                    current_type_new_status = False
                else:
                    current_type_new_status = True
                self.user.available_push_notifications_types = self.user.available_push_notifications_types.replace('"%s":%s' % (type, str(current_type_status).lower()), '"%s":%s' % (type, str(current_type_new_status).lower()))
                need_commit = True
            except Exception, e:
                logger.debug(str(e))
        if need_commit:
            self.session.commit()

        return self.success(self.user.push_response)

@route('user/visible_in_find_friends')
class LetMembersFindMeUsingFindFriendsHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        return self.success({'visible_in_find_friends': self.user.visible_in_find_friends})

    def update(self):

        if self.user is None:
            die(401)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_USER_FIND_FRIENDS_VISIBILITY')
        logger.debug(self.request_object)

        visible_in_find_friends = ''

        if self.request_object:
            if 'visible_in_find_friends' in self.request_object:
                visible_in_find_friends = self.request_object['visible_in_find_friends']

        if self.user.visible_in_find_friends != visible_in_find_friends:
            if visible_in_find_friends:
                self.user.visible_in_find_friends = True
            else:
                self.user.visible_in_find_friends = False
            self.session.commit()

        return self.success({'visible_in_find_friends': self.user.visible_in_find_friends})