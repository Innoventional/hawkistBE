__author__ = 'ne_luboff'


BANK_CARD_ALREADY_USED = 'Sorry, but this card already used in Hawkist app. Check card number and try again'

ADD_CARD_EMPTY_FIELDS = 'You must select a %s in order to add bank card.'
ADD_CARD_NO_STRIPE_TOKEN = 'No stripe token in request'

UPDATE_CARD_EMPTY_FIELDS = 'You must select a %s in order to update bank card.'
UPDATE_CARD_NO_ID = 'No card to update id'
UPDATE_CARD_INVALID_ID = 'Invalid stripe card id (%s)'

DELETE_CARD_NO_CARD_ID = 'No card to delete id'

CREATE_CHARGE_NO_CARD_ID = 'You must select card to buy the listing'
CREATE_CHARGE_NO_LISTING_ID = 'No listing to buy id'
CREATE_CHARGE_NO_STRIPE_ACCOUNT = 'First add bank card'

CREATE_CHARGE_BUY_YOUR_OWN_LISTING = 'Sorry, but you cannot buy your own listings'
CREATE_CHARGE_BUY_RESERVED_LISTING = 'Sorry, but this listing is reserved'
CREATE_CHARGE_BUY_SOLD_LISTING = 'Sorry, but this listing is sold out'