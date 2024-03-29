import logging
import datetime
from api.feedbacks.models import Feedback, FeedbackType
from api.orders.models import UserOrders, SortingStatus
from api.users.models import User
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.feedback_errors import FEEDBACK_NO_ORDER_ID, FEEDBACK_NOT_AVAILABLE, FEEDBACK_NO_TEXT, \
    FEEDBACK_NO_TYPE, FEEDBACK_INVALID_TYPE
from ui_messages.errors.orders_errors import UPDATE_ORDER_NO_ORDER
from ui_messages.errors.users_errors.update_errors import NO_USER_WITH_ID
from utility.notifications import notification_new_feedback, update_notification_order_available_feedback
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/feedbacks/(.*)')
class FeedbackHandler(ApiHandler):
    allowed_methods = ('GET', 'POST')

    def read(self, user_id):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        user = self.session.query(User).get(user_id)

        if not user:
            return self.make_error(NO_USER_WITH_ID % user_id)

        return self.success({
            'feedbacks': {
                'positive': [f.response for f in user.feedbacks if f.type == FeedbackType.Positive],
                'neutral': [f.response for f in user.feedbacks if f.type == FeedbackType.Neutral],
                'negative': [f.response for f in user.feedbacks if f.type == FeedbackType.Negative]
            }
        })

    def create(self, user_id):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug(self.request_object)

        user = self.session.query(User).get(user_id)
        if not user:
            return self.make_error(NO_USER_WITH_ID % user_id)

        order_id = ''
        text = ''
        feedback_type = ''

        if self.request_object:
            if 'order_id' in self.request_object:
                order_id = self.request_object['order_id']

            if 'text' in self.request_object:
                text = self.request_object['text']

            if 'type' in self.request_object:
                feedback_type = self.request_object['type']

        if not order_id:
            return self.make_error(FEEDBACK_NO_ORDER_ID)

        order = self.session.query(UserOrders).get(order_id)
        if not order:
            return self.make_error(UPDATE_ORDER_NO_ORDER % order_id)

        if not order.available_feedback:
            return self.make_error(FEEDBACK_NOT_AVAILABLE)

        if not text:
            return self.make_error(FEEDBACK_NO_TEXT)

        if len(str(feedback_type)) == 0:
            return self.make_error(FEEDBACK_NO_TYPE)

        if str(feedback_type) not in ['0', '1', '2']:
            return self.make_error(FEEDBACK_INVALID_TYPE)

        new_feedback = Feedback()
        new_feedback.created_at = datetime.datetime.utcnow()
        new_feedback.updated_at = datetime.datetime.utcnow()

        new_feedback.user_id = self.user.id
        new_feedback.to_user_id = user_id
        new_feedback.text = text.encode('utf-8')
        new_feedback.type = feedback_type

        self.session.add(new_feedback)

        order.available_feedback = False
        order.sorting_status = SortingStatus.Close

        update_notification_order_available_feedback(self, order_id)

        # calculate user rating
        # get all feedbacks
        feedbacks = user.feedbacks
        positive = 0
        negative = 0
        neutral = 0
        for f in feedbacks:
            if f.type == FeedbackType.Positive:
                positive += 1
            elif f.type == FeedbackType.Negative:
                negative += 1
            else:
                neutral += 1

        # get percent value
        rating_percentage = (positive + 0.5 * neutral - negative) / feedbacks.count()

        # percentage to stars
        # 0 - 0.19 -> 1
        # 0.2 - 0.39 -> 2
        # 0.4 - 0.59 -> 3
        # 0.6 - 0.79 -> 4
        # 0.8 - 1 -> 5

        rating = 1
        if 0.2 <= rating_percentage < 0.4:
            rating = 2
        elif 0.4 <= rating_percentage < 0.6:
            rating = 3
        elif 0.6 <= rating_percentage < 0.8:
            rating = 4
        elif rating_percentage >= 0.8:
            rating = 5

        user.rating = rating
        notification_new_feedback(self, order.listing, feedback_type)

        self.session.commit()

        return self.success()



