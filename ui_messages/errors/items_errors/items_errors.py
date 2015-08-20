# -*- coding: utf-8 -*-

__author__ = 'ne_luboff'

GET_LISTING_INVALID_ID = 'No listing with id %s'
GET_LISTING_BY_USER_INVALID_ID = 'No user with id %s'

# Create new listing
CREATE_LISTING_USER_HAVENT_FB = "Sorry, but you cannot sell on Hawkist until you have connected a Facebook account."
CREATE_LISTING_USER_DONT_CONFIRM_EMAIL = "Sorry, but you cannot sell on Hawkist until you have confirmed an email " \
                                         "address."
CREATE_LISTING_EMPTY_FIELDS = 'You must input the %s in order to create a listing.'

# check is this instance exist
INVALID_PLATFORM_ID = 'No platform with id %s'
INVALID_CATEGORY_ID = 'No category with id %s'
INVALID_SUBCATEGORY_ID = 'No subcategory with id %s'
INVALID_COLOUR_ID = 'No colour with id %s'
INVALID_CONDITION_ID = 'No condition with id %s'

# check nesting
WRONG_PLATFORM_CATEGORY_RELATION = "Platform %s has no Category %s (%s). Try again"
WRONG_CATEGORY_SUBCATEGORY_RELATION = "Category %s (%s) has no Subcategory %s (%s > %s). Try again"
WRONG_SUBCATEGORY_COLOUR_RELATION = "Subcategory %s (%s > %s) has no Colour %s (%s > %s > %s). Try again"
WRONG_SUBCATEGORY_CONDITION_RELATION = "Subcategory %s (%s > %s) has no Condition %s (%s > %s > %s). Try again"

# validate create new listing data
CREATE_LISTING_RETAIL_PRICE_LESS_THAN_1 = u'Retail price must be greater than £1'
CREATE_LISTING_RETAIL_PRICE_LESS_THAN_SELLING_PRICE = "Retail price must be greater than selling price"
CREATE_LISTING_TOO_MANY_PHOTOS = 'You can add only 4 photos'

# Delete the listing
DELETE_LISTING_NO_ID = 'No listing to delete id'
DELETE_LISTING_ANOTHER_USER = 'Sorry, but you cannot delete this item because you are not owner of it'
DELETE_RESERVED_LISTING = 'You cannot delete reserved listing'
DELETE_SOLD_LISTING = 'You cannot delete sold listing'

# update listing
UPDATE_LISTING_UNDEFINED_LISTING_ID = 'No listing to update id'
UPDATE_LISTING_LISTING_SOLD = 'You cannot update sold listing'
UPDATE_LISTING_EMPTY_FIELDS = 'You must select the %s in order to update a listing.'
UPDATE_LISTING_SELLING_PRICE_MUST_BE_LESS_THAN_RETAIL = u'Selling price must be less than £%s'

# Listing likes
LIKE_LISTING_NO_ID = 'No listing to like id'
LIKE_YOUR_OWN_LISTING = 'You cannot add your own listings to wishlist'