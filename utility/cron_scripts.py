import datetime
import logging
from api.items.models import Listing, ListingStatus, ListingPhoto
from api.offers.models import OfferStatus
from api.orders.models import UserOrders, OrderStatus
from api.tags.models import Platform
from api.users.models import User, SystemStatus
from environment import env
from orm import new_session
from utility.amazon import delete_file_from_s3
from utility.average_response_time import calculate_average_response_time
from utility.notifications import notification_item_received, notification_funds_released
from utility.send_email import send_warning_4_6_days_email, funds_received_seller
import boto

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


def daily_events():
    """
    Daily events are:
        - send warnings and notifications on 4th and 6th days to buyer "Is item received?"
        - automatic money release on 7th day to seller.
    """
    with new_session() as session:
        """
        Send all messages.
        Function for sending 4/6 days notification to email and user notification screen if order is active
        """
        logger.debug('Cron script started: %s' % datetime.datetime.utcnow())
        orders = session.query(UserOrders).filter(UserOrders.order_status == OrderStatus.Active)
        for order in orders:
            # check time difference
            time_delta = datetime.datetime.utcnow() - order.created_at
            if time_delta.days == 4 or time_delta.days == 6:
                # send 4/6 days warning letter
                send_warning_4_6_days_email(order.user.email, order.user.username, order.listing.title, time_delta.days)
                # add notifications
                notification_item_received(session, order)
            elif time_delta.days == 7:
                # first we must transfer money from pending balance to available
                order.listing.user.app_wallet_pending -= order.payment_sum_without_application_fee
                order.listing.user.app_wallet += order.payment_sum_without_application_fee
                order.order_status = OrderStatus.FundsReleasedByTimer
                # send email notification to seller
                funds_received_seller(order)
                # add notification
                notification_funds_released(session, order.user, order.listing)
        session.commit()


def hourly_events():
    with new_session() as session:
        """
        Check all reserved listings
        """
        listings = session.query(Listing).filter(Listing.reserved_by_user == True)
        for listing in listings:
            time_delta = datetime.datetime.utcnow() - listing.reserve_time
            if time_delta.days >= 1:
                # make this listing available
                listing.selling_price = listing.previous_price
                listing.reserved_by_user = False
                listing.status = ListingStatus.Active
                listing.user_who_reserve_id = None
                listing.user_who_reserve = None
                listing.reserve_time = None

            # make hidden offers visible
            for offer in listing.listing_offers:
                if offer.status == OfferStatus.Active and not offer.visibility:
                    offer.visibility = True
        """
        Recalculate response time for every user
        """
        users = session.query(User).filter(User.system_status == SystemStatus.Active)
        for user in users:
            user.average_response_time = calculate_average_response_time(user)
        session.commit()
        logger.debug('Cron script finished: %s' % datetime.datetime.utcnow())


def clear_amazon_s3_bucket():
    """
    Compare images in Amazon S3 bucket and DB.
    If image is not in use delete it.
    """
    AWS_ACCESS_KEY_ID = env['amazon']['access_key_id']
    AWS_SECRET_ACCESS_KEY = env['amazon']['secret_access_key']
    user_images_bucket_name = 'hawkist-avatar'
    listing_images_bucket_name = 'hawkist-item-images'
    link_to_user_images_bucket = 'http://{0}.s3.amazonaws.com/'.format(user_images_bucket_name)
    link_to_listing_images_bucket = 'https://s3-eu-west-1.amazonaws.com/{0}/'.format(listing_images_bucket_name)

    # create connection to S3
    s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    # get all user images (avatars and thumbnails)
    user_images_bucket = s3.get_bucket(user_images_bucket_name)
    user_images_bucket_names = [o.key for o in user_images_bucket.list()]

    # get all listing images
    listing_images_bucket = s3.get_bucket(listing_images_bucket_name)
    listing_images_bucket_names = [o.key for o in listing_images_bucket.list()]

    # get data from db
    with new_session() as session:
        all_users = session.query(User)
        user_avatar_db_names = [user.avatar.split('?')[0].replace(link_to_user_images_bucket, '')
                                for user in all_users]
        user_thumbnail_db_names = [user.thumbnail.split('?')[0].replace(link_to_user_images_bucket, '')
                                   for user in all_users]
        platform_images_db_names = [platform.image_url.split('?')[0].replace(link_to_user_images_bucket, '')
                                    for platform in session.query(Platform)]
        listing_images_db_names = [listing_photo.image_url.split('?')[0].replace(link_to_listing_images_bucket, '')
                                   for listing_photo in session.query(ListingPhoto)]

    # first check avatars
    for user_image_name in user_images_bucket_names:
        if user_image_name not in user_avatar_db_names and user_image_name not in user_thumbnail_db_names \
                and user_image_name not in platform_images_db_names:
            # delete this image from bucket
            delete_file_from_s3(user_images_bucket_name, user_image_name)

    for listing_image_name in listing_images_bucket_names:
        if listing_image_name not in listing_images_db_names:
            delete_file_from_s3(listing_images_bucket_name, listing_image_name)