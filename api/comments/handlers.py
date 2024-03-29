import logging
import datetime
from sqlalchemy import func, and_
from api.comments.models import Comment
from api.items.models import Listing
from api.users.models import SystemStatus, User
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.comments_errors.comments_errors import GET_COMMENTS_NO_LISTING_ID, CREATE_COMMENTS_NO_LISTING_ID, \
    CREATE_COMMENTS_EMPTY_DATA, CREATE_COMMENTS_ON_BLOCKED_USER
from ui_messages.errors.items_errors.items_errors import GET_LISTING_INVALID_ID
from ui_messages.errors.users_errors.blocked_users_error import GET_BLOCKED_USER_COMMENTS
from ui_messages.errors.users_errors.suspended_users_errors import GET_SUSPENDED_USER_COMMENTS
from ui_messages.messages.custom_error_titles import GET_DELETED_LISTING_TITLE
from utility.comments import get_users_from_comment
from utility.notifications import notification_new_comment, notification_new_mention
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('listings/comments/(.*)')
class ItemCommentsHandler(ApiHandler):
    allowed_methods = ('GET', 'POST')

    def read(self, listing_id):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error
        
        update_user_last_activity(self)

        if not listing_id:
            return self.make_error(GET_COMMENTS_NO_LISTING_ID)

        # check is listing id int
        try:
            int(listing_id)
        except:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        listing = self.session.query(Listing).get(listing_id)

        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        # check has current user access to this listing comments
        if self.user in listing.user.blocked:
            return self.make_error(message=GET_BLOCKED_USER_COMMENTS % listing.user.username.upper(),
                                   status=3)

        # check is user active
        if listing.user.system_status == SystemStatus.Suspended:
            return self.make_error(GET_SUSPENDED_USER_COMMENTS % listing.user.username.upper())

        # listing_comments = self.session.query(Comment).filter(Comment.listing_id == listing_id).order_by(Comment.created_at)
        return self.success({'comments': [c.response for c in listing.listing_comments]})

    def create(self, listing_id):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_NEW_COMMENT')
        logger.debug(self.request_object)

        # first validate listing
        if not listing_id:
            return self.make_error(CREATE_COMMENTS_NO_LISTING_ID)

        listing = self.session.query(Listing).get(listing_id)

        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        # check has current user access to this listing comments
        if self.user in listing.user.blocked:
            return self.make_error(message=GET_BLOCKED_USER_COMMENTS % listing.user.username.upper(),
                                   status=3)

        if listing.user in self.user.blocked:
            return self.make_error(message=CREATE_COMMENTS_ON_BLOCKED_USER % listing.user.username,
                                   title=GET_DELETED_LISTING_TITLE)

        # check is user active
        if listing.user.system_status == SystemStatus.Suspended:
            return self.make_error(GET_SUSPENDED_USER_COMMENTS % listing.user.username.upper())

        text = None

        # next validate input data
        if self.request_object:
            if 'text' in self.request_object:
                text = self.request_object['text']

        if not text:
            return self.make_error(CREATE_COMMENTS_EMPTY_DATA)

        # finally create comment
        comment = Comment()
        comment.created_at = datetime.datetime.utcnow()
        comment.listing = listing
        comment.user = self.user
        text = text.encode('utf-8')
        comment.text = text
        # try extract mentioned users from comment text
        mentioned_user_usernames = get_users_from_comment(text)
        if mentioned_user_usernames:
            # check every username
            for mentioned_user_username in mentioned_user_usernames:
                # first try get user by username
                user_to_mention = self.session.query(User).filter(func.lower(User.username) == mentioned_user_username.lower()).first()
                if user_to_mention:
                    # add new mention if this user don't mention in this comment already
                    if comment not in user_to_mention.comment_mentions:
                        user_to_mention.comment_mentions.append(comment)
                    notification_new_mention(self, user_to_mention.id, listing)
        self.session.add(comment)
        self.session.commit()

        # also add notification about new comment
        if str(listing.user_id) != str(self.user.id):
            notification_new_comment(self, listing, comment)

        return self.success()


@route('listings/comments_people')
class ItemCommentsPeopleHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        q = self.get_argument('q')
        qs = []

        if q:
            qs = self.session.query(User).filter(and_(User.username.ilike(u'{0}%'.format(q)),
                                                      User.system_status == SystemStatus.Active)).order_by(User.id)

        response = {
            'status': 0,
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'avatar': user.avatar
                } for user in qs]
        }
        logger.debug(response)
        return response