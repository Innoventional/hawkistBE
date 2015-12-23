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
    except Exception, e:
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


def get_facebook_friends(token):
    """
    Getting facebook friends in api
    """
    friends = []
    error = None
    try:
        opener = urllib2.build_opener()
        # get friends
        url = 'https://graph.facebook.com/me/friends?access_token={0}'.format(token)
        response = opener.open(url).read()
        response_dict = json.loads(response)
        logger.debug('Facebook friend response')
        logger.debug(response_dict)
        for f in response_dict['data']:
            friends.append(f['id'])
        # print response_dict
    except urllib2.HTTPError, e:
        error = str(e)
    finally:
        return {
            'data': friends,
            'error': error
        }

if __name__ == '__main__':
    print get_facebook_friends('CAAGbgG3gWzEBAML5O1TUvGhYu0PCNJNmWMcEptI9u679GvVZCXJmIaRIybAMx44JgTEM8sJ5PZAVjddcUZBzASXsuadnDtSQYJMgLex1TTV3nAnA5KkzESfelMcixXjaJ1g5kwAJ74g8MkSZCXbyVo1rDBhVEZBlQvNLdZAxTKBYNEmxqL7kGRwLStX8oLIkiDnNe85tsm7fGyueGwPtaM7cPL3lgxaMSEomb5BJn01hfyvWvmjebX')
