import json
import logging
import urllib2

logger = logging.getLogger(__name__)


def get_facebook_user(token):
    """
    Use facebook graph api for getting info about user.
    Facebook response will be successful if token is valid.
    Get current (depending on token) user id in our application,
    email and username (which contains of first name and last name).
    """
    data = {}
    error = None
    try:
        opener = urllib2.build_opener()
        url = 'https://graph.facebook.com/me/?access_token={0}'.format(token)
        response = opener.open(url).read()
        response_dict = json.loads(response)
        logger.debug('FB response')
        logger.debug(response_dict)
        try:
            data['id'] = response_dict['id']
            data['email'] = response_dict['email']
            data['username'] = response_dict['name']
        except Exception, e:
            if str(e) == "'email'":
                error = 'Add email address to facebook first'
            else:
                error = 'Facebook response have not key %s' % str(e)
    except urllib2.HTTPError, e:
        error = str(e)
    finally:
        return {
            'data': data,
            'error': error
        }


def get_facebook_photo(token):
    """
    Special requests for getting facebook avatar and thumbnail icon.
    """
    photo = dict()
    error = None
    try:
        opener = urllib2.build_opener()
        # get avatar
        url = 'https://graph.facebook.com/me/picture?type=large&redirect=0&access_token={0}'.format(token)
        response = opener.open(url).read()
        response_dict = json.loads(response)
        logger.debug('Avatar response')
        logger.debug(response_dict)
        photo['avatar'] = response_dict['data']['url']
        # get thumbnail
        url = 'https://graph.facebook.com/me/picture?type=square&redirect=0&access_token={0}'.format(token)
        response = opener.open(url).read()
        response_dict = json.loads(response)
        logger.debug('Thumbnail response')
        logger.debug(response_dict)
        photo['thumbnail'] = response_dict['data']['url']
    except urllib2.HTTPError, e:
        error = str(e)
    finally:
        return {
            'data': photo,
            'error': error
        }

if __name__ == '__main__':
    print get_facebook_user('CAACEdEose0cBAD54FnGjjaQpcZCZAofYxyASxhWsK6teG1B50kcmZChjdqZBwjPKrk7WSgH7XwoZAWcem8efejjHa3McVMZAnRmKFtnUgL3ZCYa83ZBKZB3wYqPC9ZCDrjGgCsGNixzo1iWUzOt1UPgn4NQKwoWPQ2mUVp1XEeEVJn8mqIpQujRXrd6qdzkYxhLO7pSRuDAHgC5eZBdlzCnMzYVKstCKkFlzcMZD')
