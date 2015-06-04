import json
import logging
import urllib2

logger = logging.getLogger(__name__)


def get_facebook_user(token):
    user_id = ''
    error = None
    try:
        opener = urllib2.build_opener()
        url = 'https://graph.facebook.com/me/?access_token={0}'.format(token)
        response = opener.open(url).read()
        response_dict = json.loads(response)
        try:
            user_id = response_dict['id']
        except Exception, e:
            logger.debug('Facebook response have not key %s' % str(e))
    except urllib2.HTTPError, e:
        error = str(e)
    finally:
        return {
            'data': user_id,
            'error': error
        }


def get_facebook_photo(token):
    photo = dict()
    error = None
    try:
        opener = urllib2.build_opener()
        # get avatar
        url = 'https://graph.facebook.com/me/picture?type=large&redirect=0&access_token={0}'.format(token)
        response = opener.open(url).read()
        response_dict = json.loads(response)
        photo['avatar'] = response_dict['data']['url']
        # get thumbnail
        url = 'https://graph.facebook.com/me/picture?type=square&redirect=0&access_token={0}'.format(token)
        response = opener.open(url).read()
        response_dict = json.loads(response)
        photo['thumbnail'] = response_dict['data']['url']
    except urllib2.HTTPError, e:
        error = str(e)
    finally:
        return {
            'data': photo,
            'error': error
        }

if __name__ == '__main__':
    print get_facebook_user('CAAWeYZAnzPmcBAAl4UhOObK3ZAKp91EiDp6ZCX4H1wQyPBWlheGY1jmnn4og8SlPzs2Km0vAtlmgmKoZAgeer2M3mSLgZAIs1ZABkZAceYSPkj8XVf6u5uBRUvY1JcRMM5oWVVactBKowtTW7C3DLKRtrRvhj8iRbRtRDyBNSXMOSuCtfAn71TE01wonO1odOXtHDwmF8NAVd0NlmF6l6E0z7pkUtQ3FlJvwL4jEHyJVqEYTSt2NScd')
