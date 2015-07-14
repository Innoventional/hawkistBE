# -*- coding: utf-8 -*-

__author__ = 'ne_luboff'

GET_LISTING_INVALID_ID = 'No listing with id %s'
GET_LISTING_BY_USER_INVALID_ID = 'No user with id %s'

# Create new listing
CREATE_LISTING_USER_HAVENT_FB = "Sorry, but you can't sale anything because you don't link your FB account"
CREATE_LISTING_USER_DONT_CONFIRM_EMAIL = "Sorry, but you can't sale anything because you don't confirm your email."
CREATE_LISTING_EMPTY_FIELDS = 'You must select a %s in order to create a listing.'

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
