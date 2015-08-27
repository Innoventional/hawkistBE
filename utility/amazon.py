import logging
from boto import connect_s3
from boto.s3.key import Key

# ne_luboff's aws credentials
# AWS_S3_BUCKET = 'social-avatars'
# AWS_ACCESS_KEY_ID = 'AKIAJKHWEWJIUIOFQTQA'
# AWS_SECRET_ACCESS_KEY = '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'

# hawkist live aws credentials
AWS_S3_BUCKET = 'hawkist-avatar'
AWS_S3_BUCKET_WITHDRAWALS = 'hawkist-withdrawals'
AWS_ACCESS_KEY_ID = 'AKIAJZDNOKN3IAAMLYJQ'
AWS_SECRET_ACCESS_KEY = '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'

LOCAL_PATH = '/backup/s3/'

boto_logger = logging.getLogger('boto')


def push_image_to_s3(fname):
    try:
        bucket_name = AWS_S3_BUCKET
        # connect to the bucket
        conn = connect_s3(AWS_ACCESS_KEY_ID,
                          AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(bucket_name)
        # go through each version of the file
        key = fname.split('/')[-1]
        # create a key to keep track of our file in the storage
        k = Key(bucket)
        k.key = key
        k.set_contents_from_filename(fname)
        # we need to make it public so it can be accessed publicly
        k.make_public()
        # image will be available at http://your_bucket.s3.amazonaws.com/your_image.jpg
        return True
    except Exception as e:
        boto_logger.error('Image pushing to Amazon s3 failed, error: %s' % str(e))
        return False


import boto
from boto.s3.key import Key


def upload_file(filename, data, content_type='image/jpeg'):
    try:
        s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        bucket = s3.get_bucket(AWS_S3_BUCKET)
        k = Key(bucket)

        k.key = '{0}.jpeg'.format(filename)

        if content_type:
            k.content_type = content_type

        k.set_contents_from_string(data, policy='public-read')
        expires = 60 * 60 * 24 * 360 * 10

        return k.generate_url(expires, force_http=True)
    except Exception as e:
        boto_logger.error('Image pushing to Amazon s3 failed, error: %s' % str(e))
        return ''


def upload_file_withdrawals(filename, data, content_type='csv'):
    try:
        s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        bucket = s3.get_bucket(AWS_S3_BUCKET_WITHDRAWALS)
        k = Key(bucket)

        k.key = '{0}.csv'.format(filename)

        if content_type:
            k.content_type = content_type

        k.set_contents_from_string(data, policy='public-read')
        expires = 60 * 60 * 24 * 360 * 10

        return k.generate_url(expires, force_http=True)
    except Exception as e:
        boto_logger.error('File pushing to Amazon s3 failed, error: %s' % str(e))
        return ''