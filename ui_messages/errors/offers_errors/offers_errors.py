# -*- coding: utf-8 -*-
from environment import env

__author__ = 'ne_luboff'

REACH_OFFER_LIMIT = 'You cannot create more than %s offers per day.' % env['offer_limit_per_day']

GET_OFFERS_NO_LISTING_ID = 'Get offers no listing id'
GET_OFFERS_ANOTHER_OWNER = 'Access denied. You cannot get offers of another user listing'

CREATE_OFFER_YOU_OWN_LISTING = 'Sorry but you cannot make offers for your own listings'
CREATE_OFFER_NO_LISTING_ID = 'Create offer no listing id'
CREATE_OFFER_EMPTY_DATA = 'You must input new price'

CREATE_OFFER_OFFERED_PRICE_MUST_BE_LESS_THAN_RETAIL = u'You cannot offer a price which is greater than £%s.'

UPDATE_OFFER_NO_OFFER_ID = 'You must select offer to update (no offer id).'
UPDATE_OFFER_NO_NEW_STATUS = 'You must select new offer status.'
UPDATE_OFFER_INVALID_OFFER_ID = 'No offer with id %s'
UPDATE_OFFER_INVALID_STATUS = 'Invalid new offer status.'
