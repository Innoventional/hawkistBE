import datetime

__author__ = 'ne_luboff'


def calculate_average_response_time(user):
    notifications = user.user_notifications
    average_response_time = 0
    if notifications.count() > 0:
        # first check is unseen notifications
        for n in notifications:
            if not n.seen_at:
                n.response_time = (datetime.datetime.utcnow() - n.created_at).total_seconds()
        average_response_time = sum(u.response_time for u in notifications) / notifications.count()
    return average_response_time
