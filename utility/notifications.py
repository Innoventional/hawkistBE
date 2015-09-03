import datetime
import json
from sqlalchemy import and_
from api.notifications.models import UserNotificantion, NotificationType, NotificationPriority
from api.users.models import User
from ui_messages.messages.push_notifications import NEW_COMMENTS, ITEM_SOLD, ITEM_RECEIVED, NEW_FEEDBACK, FUNDS_RELEASED, \
    LEAVE_FEEDBACK, ITEM_IS_FAVOURITED, A_FAVOURITE_ITEM_IS_SOLD, NEW_FOLLOWERS, NEW_ITEMS, MENTIONS, NEW_OFFERED_PRICE, \
    OFFERED_PRICE_ACCEPTED, OFFERED_PRICE_DECLINED

__author__ = 'ne_luboff'


def check_is_pushes_available_by_type(user, push_type):
    if user.apns_token and user.available_push_notifications and json.loads(json.loads(json.dumps(user.available_push_notifications_types))).get(push_type):
        return True
    return False


def notification_new_comment(self, listing, comment):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = listing.user_id
    notification.type = NotificationType.NewComment
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.comment_id = comment.id
    notification.comment_text = comment.text
    notification.priority = NotificationPriority.High
    self.session.add(notification)
    self.session.commit()

    if check_is_pushes_available_by_type(listing.user, '0'):
        listing.user.notify(alert=NEW_COMMENTS % listing.title,
                            custom={'type': '0',
                                    'listing_id': listing.id},
                            sound='',
                            badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == listing.user_id,
                                                                                    UserNotificantion.seen_at == None)).count())


def notification_item_sold(self, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = listing.user_id
    notification.type = NotificationType.ItemSold
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.High
    self.session.add(notification)
    self.session.commit()

    if check_is_pushes_available_by_type(listing.user, '1'):
        listing.user.notify(alert=ITEM_SOLD % listing.title,
                            custom={'type': '1'},
                            sound='',
                            badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == listing.user_id,
                                                                                    UserNotificantion.seen_at == None)).count())


def notification_item_received(session, order):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = order.user.id
    notification.type = NotificationType.ItemReceived
    notification.user_id = order.listing.user.id
    notification.user_avatar = order.listing.user.avatar
    notification.user_username = order.listing.user.username
    notification.listing_id = order.listing.id
    notification.listing_title = order.listing.title
    notification.listing_photo = order.listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.High
    session.add(notification)
    session.commit()

    if check_is_pushes_available_by_type(order.user, '2'):
        order.user.notify(alert=ITEM_RECEIVED % order.listing.title,
                          custom={'type': '2'},
                          sound='',
                          badge=session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == order.user_id,
                                                                             UserNotificantion.seen_at == None)).count())


def notification_new_feedback(self, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = listing.user_id
    notification.type = NotificationType.NewFeedback
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.High
    self.session.add(notification)
    self.session.commit()

    if check_is_pushes_available_by_type(listing.user, '3'):
        listing.user.notify(alert=NEW_FEEDBACK,
                            custom={'type': '3'},
                            sound='',
                            badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == listing.user_id,
                                                                                    UserNotificantion.seen_at == None)).count())


def notification_funds_released(session, user, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = listing.user_id
    notification.type = NotificationType.FundsReleased
    notification.user_id = user.id
    notification.user_avatar = user.avatar
    notification.user_username = user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_selling_price = listing.selling_price
    notification.listing_shipping_price = listing.shipping_price
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.High
    session.add(notification)
    session.commit()

    if check_is_pushes_available_by_type(listing.user, '4'):
        listing.user.notify(alert=FUNDS_RELEASED,
                            custom={'type': '4'},
                            sound='',
                            badge=session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == listing.user_id,
                                                                               UserNotificantion.seen_at == None)).count())


def notification_leave_feedback(self, order):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = order.user.id
    notification.type = NotificationType.LeaveFeedback
    notification.user_id = order.listing.user_id
    notification.user_avatar = order.listing.user.avatar
    notification.user_username = order.listing.user.username
    notification.listing_id = order.listing.id
    notification.listing_title = order.listing.title
    notification.listing_photo = order.listing.listing_photos[0].image_url
    notification.order_id = order.id
    notification.order_available_feedback = True
    notification.priority = NotificationPriority.Low
    self.session.add(notification)
    self.session.commit()

    if check_is_pushes_available_by_type(self.user, '5'):
        order.user.notify(alert=LEAVE_FEEDBACK % order.listing.title,
                          custom={'type': '5',
                                  'order_id': order.id,
                                  'order_available_feedback': True},
                          sound='',
                          badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == order.user.id,
                                                                                  UserNotificantion.seen_at == None)).count())


def notification_item_favourite(self, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = listing.user_id
    notification.type = NotificationType.ItemIsFavourited
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.Low
    self.session.add(notification)
    self.session.commit()

    if check_is_pushes_available_by_type(listing.user, '6'):
        listing.user.notify(alert=ITEM_IS_FAVOURITED % listing.title,
                            custom={'type': '6',
                                    'user_id': self.user.id},
                            sound='',
                            badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == listing.user_id,
                                                                               UserNotificantion.seen_at == None)).count())


def notification_favourite_item_sold(self, owner_id, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner_id
    notification.type = NotificationType.AFavouriteItemIsSold
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.Low
    self.session.add(notification)
    self.session.commit()

    # get owner by id
    owner = self.session.query(User).get(owner_id)

    if check_is_pushes_available_by_type(owner, '7'):
        owner.notify(alert=A_FAVOURITE_ITEM_IS_SOLD % listing.title,
                     custom={'type': '7',
                             'listing_id': listing.id},
                     sound='',
                     badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == owner_id,
                                                                             UserNotificantion.seen_at == None)).count())


def notification_new_follower(self, following_user_id):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = following_user_id
    notification.type = NotificationType.NewFollowers
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.priority = NotificationPriority.Low
    self.session.add(notification)
    self.session.commit()

    # get owner by id
    owner = self.session.query(User).get(following_user_id)

    if check_is_pushes_available_by_type(owner, '8'):
        owner.notify(alert=NEW_FOLLOWERS,
                     custom={'type': '8',
                             'user_id': self.user.id},
                     sound='',
                     badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == following_user_id,
                                                                             UserNotificantion.seen_at == None)).count())


def notification_following_user_new_item(self, owner_id, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner_id
    notification.type = NotificationType.NewItems
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.Low
    self.session.add(notification)
    self.session.commit()

    # get owner by id
    owner = self.session.query(User).get(owner_id)

    if check_is_pushes_available_by_type(owner, '9'):
        owner.notify(alert=NEW_ITEMS,
                     custom={'type': '9',
                             'listing_id': listing.id},
                     sound='',
                     badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == owner_id,
                                                                             UserNotificantion.seen_at == None)).count())


def notification_new_mention(self, owner_id, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner_id
    notification.type = NotificationType.Mentions
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.Low
    self.session.add(notification)
    self.session.commit()

    # get owner by id
    owner = self.session.query(User).get(owner_id)

    if check_is_pushes_available_by_type(owner, '10'):
        owner.notify(alert=MENTIONS,
                     custom={'type': '10',
                             'listing_id': listing.id},
                     sound='',
                     badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == owner_id,
                                                                             UserNotificantion.seen_at == None)).count())


def notification_new_offered_price(self, listing, offered_price):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = listing.user_id
    notification.type = NotificationType.NewOfferedPrice
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.comment_offer_price = offered_price
    notification.priority = NotificationPriority.Mandatory
    self.session.add(notification)
    self.session.commit()

    if listing.user.apns_token:
        listing.user.notify(alert=NEW_OFFERED_PRICE % listing.title,
                            custom={'type': '11',
                                    'listing_id': listing.id},
                            sound='',
                            badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == listing.user_id,
                                                                                    UserNotificantion.seen_at == None)).count())


def notification_offered_price_accepted(self, owner, listing, offered_price):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner.id
    notification.type = NotificationType.OfferedPriceAccepted
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.comment_offer_price = offered_price
    notification.priority = NotificationPriority.Mandatory
    self.session.add(notification)
    self.session.commit()

    if owner.available_push_notifications and owner.apns_token:
        owner.notify(alert=OFFERED_PRICE_ACCEPTED % listing.id,
                     custom={'type': '12',
                             'listing_id': listing.id},
                     sound='',
                     badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == owner.id,
                                                                             UserNotificantion.seen_at == None)).count())


def notification_offered_price_declined(self, owner, listing, offered_price):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner.id
    notification.type = NotificationType.OfferedPriceDeclined
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.comment_offer_price = offered_price
    notification.priority = NotificationPriority.Mandatory
    self.session.add(notification)
    self.session.commit()

    if owner.available_push_notifications and owner.apns_token:
        owner.notify(alert=OFFERED_PRICE_DECLINED % listing.id,
                     custom={'type': '13',
                             'listing_id': listing.id},
                     sound='',
                     badge=self.session.query(UserNotificantion).filter(and_(UserNotificantion.owner_id == owner.id,
                                                                             UserNotificantion.seen_at == None)).count())


def update_notification_user_username(self, user):
    notifications_with_this_user = self.session.query(UserNotificantion).filter(UserNotificantion.user_id == user.id)
    if notifications_with_this_user:
        for n in notifications_with_this_user:
            n.user_username = user.username
            if n.user_avatar != user.avatar:
                n.user_avatar = user.avatar


def update_notification_user_avatar(self, user):
    notifications_with_this_user = self.session.query(UserNotificantion).filter(UserNotificantion.user_id == user.id)
    if notifications_with_this_user:
        for n in notifications_with_this_user:
            n.user_avatar = user.avatar


def update_notification_listing_title(self, listing):
    notifications_with_this_listing = self.session.query(UserNotificantion).filter(UserNotificantion.listing_id == listing.id)
    if notifications_with_this_listing:
        for l in notifications_with_this_listing:
            l.listing_title = listing.title


def update_notification_listing_photo(self, listing):
    notifications_with_this_listing = self.session.query(UserNotificantion).filter(UserNotificantion.listing_id == listing.id)
    if notifications_with_this_listing:
        for l in notifications_with_this_listing:
            l.listing_photo = listing.listing_photos[0].image_url


def update_notification_order_available_feedback(self, order_id):
    notification_with_this_order = self.session.query(UserNotificantion).filter(UserNotificantion.order_id == order_id).first()
    if notification_with_this_order:
        notification_with_this_order.order_available_feedback = False
