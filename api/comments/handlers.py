import logging
import datetime
from api.comments.models import Comment
from api.items.models import Listing
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.comments_errors.comments_errors import GET_COMMENTS_NO_LISTING_ID, CREATE_COMMENTS_NO_LISTING_ID, \
    CREATE_COMMENTS_EMPTY_DATA
from ui_messages.errors.items_errors.items_errors import GET_LISTING_INVALID_ID
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('listings/comments/(.*)')
class ItemCommentsHandler(ApiHandler):
    allowed_methods = ('GET', 'POST')

    def read(self, listing_id):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        if not listing_id:
            return self.make_error(GET_COMMENTS_NO_LISTING_ID)

        listing = self.session.query(Listing).get(listing_id)

        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        listing_comments = self.session.query(Comment).filter(Comment.listing_id == listing_id).order_by(Comment.created_at)
        return self.success({'comments': [c.response for c in listing_comments]})

    def create(self, listing_id):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_NEW_COMMENT')
        logger.debug(self.request_object)

        # first validate listing
        if not listing_id:
            return self.make_error(CREATE_COMMENTS_NO_LISTING_ID)

        listing = self.session.query(Listing).get(listing_id)

        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        text = None
        image_url = None

        # next validate input data
        if self.request_object:
            if 'text' in self.request_object:
                text = self.request_object['text']

            if 'image_url' in self.request_object:
                image_url = self.request_object['image_url']

        if not text and not image_url:
            return self.make_error(CREATE_COMMENTS_EMPTY_DATA)

        # finally create comment
        comment = Comment()
        comment.created_at = datetime.datetime.utcnow()
        comment.listing = listing
        comment.user = self.user
        comment.text = text
        comment.image_url = image_url
        self.session.add(comment)
        self.session.commit()
        return self.success()
