import os.path as op
from apns import APNs, Payload
import logging

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)

DEV_KEYS_FILE = op.abspath(op.join(op.dirname(__file__), 'certificates/hawkist-apns-dev-cert.pem'))
KEYS_FILE = op.abspath(op.join(op.dirname(__file__), 'certificates/hawkist-apns-prod-cert.pem'))

assert op.exists(KEYS_FILE)


def get_server(use_sandbox=False, keys_file=KEYS_FILE):
    """
    Create and return production or develop server.
    """
    return APNs(use_sandbox=use_sandbox, cert_file=keys_file, key_file=keys_file)


def send_ios_notify(token, server=None, **payloads):
    logger.debug(payloads)
    server = server or get_server(use_sandbox=False, keys_file=KEYS_FILE)
    server.gateway_server.send_notification(token, Payload(**payloads))

    # duplicate request for dev profiles
    server = get_server(use_sandbox=True, keys_file=DEV_KEYS_FILE)
    return server.gateway_server.send_notification(token, Payload(**payloads))


def get_feedbacks(server):
    """
    Get inactive tokens.
    """
    return list(server.feedback_server.items())


if __name__ == '__main__':
    import datetime
    # result = send_ios_notify('f18b174eb350e4ee95bf79c332146dd80a3c66bd6bd73b164718876af0cd3b2c',
    result = send_ios_notify('ab6a605a45bf9d5b4f44087b4d49c5555e492a67c190d02a4858ae1fea91525f',
                             alert='Hi', badge=1, custom={})
                             # alert='%s' % datetime.datetime.utcnow(), badge=0, custom={'type': '2'})
    # result = send_ios_notify('f18b174eb350e4ee95bf79c332146dd80a3c66bd6bd73b164718876af0cd3b2c', custom={'order_id': 220,
    #                                          'user_id': 177,
    #                                          'type': '5',
    #                                          'order_available_feedback': True},
    #                               badge=2919111, alert='Leave feedback on your recent purchase MacBook Air.')
    print result