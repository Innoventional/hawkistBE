__author__ = 'ne_luboff'

# Try get by id user which doesn't exist
NO_USER_WITH_ID = 'No user with id %s'

UPDATE_USER_INFO_NO_USERNAME = 'Username is required'
UPDATE_USER_INFO_NO_EMAIL = 'Email is required'

UPDATE_USER_INFO_USERNAME_ALREADY_USED = "Sorry, username %s already used by another user"

# email confirmation
INVALID_CONFIRM_EMAIL_LINK = 'Invalid confirmation link. Try again later'

# link fb to profile
UPDATE_USER_LINK_FB_NO_TOKEN = 'No facebook token'
UPDATE_USER_FB_ALREADY_USED = 'This facebook account is already used by another user.'

UPDATE_USER_PHONE_ALREADY_USED = 'Sorry, phone number %s already used by another user'

# user tags
UPDATE_USER_TAGS_NO_TAG_ID = 'No tag id'
UPDATE_USER_TAGS_NO_TAG_TYPE = 'No tag type'
UPDATE_USER_TAGS_INVALID_TAG_ID = 'Tag id must be a number (you entered %s)'
UPDATE_USER_TAGS_INVALID_TAG_TYPE = 'Invalid metatag type. Valid types:\n' \
                                    '0 - platform, \n1 - category, \n2 - subcategory'
UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS = '%s which you try add does not exists. Update tag list and try again'
UPDATE_USER_TAGS_TAG_ALREADY_ADDED = 'You already added %s %s to your feeds'

UPDATE_USER_TAGS_NO_EXISTING_USER_TAG = 'You can not delete %s tag %s from your feeds because you have not this tag ' \
                                        'there'
