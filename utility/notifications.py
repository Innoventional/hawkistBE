import datetime
from api.notifications.models import UserNotificantion, NotificationType, NotificationPriority

__author__ = 'ne_luboff'


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


def notification_item_received(session, owner_id, listing):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner_id
    notification.type = NotificationType.ItemReceived
    notification.user_id = listing.user.id
    notification.user_avatar = listing.user.avatar
    notification.user_username = listing.user.username
    notification.listing_id = listing.id
    notification.listing_title = listing.title
    notification.listing_photo = listing.listing_photos[0].image_url
    notification.priority = NotificationPriority.High
    session.add(notification)
    session.commit()


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


def notification_leave_feedback(self, order):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = order.listing.user_id
    notification.type = NotificationType.LeaveFeedback
    notification.user_id = self.user.id
    notification.user_avatar = self.user.avatar
    notification.user_username = self.user.username
    notification.listing_id = order.listing.id
    notification.listing_title = order.listing.title
    notification.listing_photo = order.listing.listing_photos[0].image_url
    notification.order_id = order.id
    notification.priority = NotificationPriority.Low
    self.session.add(notification)
    self.session.commit()


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


def notification_offered_price_accepted(self, owner_id, listing, offered_price):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner_id
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


def notification_offered_price_declined(self, owner_id, listing, offered_price):
    notification = UserNotificantion()
    notification.created_at = datetime.datetime.utcnow()
    notification.owner_id = owner_id
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


def update_notification_user_username(self, user):
    notifications_with_this_user = self.session.query(UserNotificantion).filter(UserNotificantion.user_id == user.id)
    if notifications_with_this_user:
        for n in notifications_with_this_user:
            n.user_username = user.username
            if n.user_avatar != user.avatar:
                n.user_avatar = user.avatar
        # self.session.commit()


def update_notification_user_avatar(self, user):
    notifications_with_this_user = self.session.query(UserNotificantion).filter(UserNotificantion.user_id == user.id)
    if notifications_with_this_user:
        for n in notifications_with_this_user:
            n.user_avatar = user.avatar
        # self.session.commit()


def update_notification_listing_title(self, listing):
    notifications_with_this_listing = self.session.query(UserNotificantion).filter(UserNotificantion.listing_id == listing.id)
    if notifications_with_this_listing:
        for l in notifications_with_this_listing:
            l.listing_title = listing.title
        # self.session.commit()


def update_notification_listing_photo(self, listing):
    notifications_with_this_listing = self.session.query(UserNotificantion).filter(UserNotificantion.listing_id == listing.id)
    if notifications_with_this_listing:
        for l in notifications_with_this_listing:
            l.listing_photo = listing.listing_photos[0].image_url
        # self.session.commit()