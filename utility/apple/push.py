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
    # result = send_ios_notify('f18b174eb350e4ee95bf79c332146dd80a3c66bd6bd73b164718876af0cd3b2c',
    result = send_ios_notify('35ca4ca211290f75ba046612de3a18246cd41322608365d0e32cb64ceaa00bc4',
                             alert='Daaaa!', badge=0)
    print result