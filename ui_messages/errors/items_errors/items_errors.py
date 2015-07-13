# -*- coding: utf-8 -*-

__author__ = 'ne_luboff'

GET_LISTING_INVALID_ID = 'No item with id %s'

# Create new listing
CREATE_LISTING_EMPTY_FIELDS = 'You must select a %s in order to create a listing.'

# check is this instance exist
INVALID_PLATFORM_ID = 'No platform with id %s'
INVALID_CATEGORY_ID = 'No category with id %s'
INVALID_SUBCATEGORY_ID = 'No subcategory with id %s'
INVALID_COLOUR_ID = 'No colour with id %s'
INVALID_CONDITION_ID = 'No condition with id %s'

# check nesting
WRONG_PLATFORM_CATEGORY_RELATION = "Platform tag %s hasn't category %s (%s). Try again"
WRONG_CATEGORY_SUBCATEGORY_RELATION = "Category tag %s (%s) hasn't subcategory %s (%s > %s). Try again"
WRONG_SUBCATEGORY_COLOUR_RELATION = "Subcategory tag %s (%s > %s) hasn't color %s (%s > %s > %s). Try again"
WRONG_SUBCATEGORY_CONDITION_RELATION = "Subcategory tag %s (%s > %s) hasn't condition %s (%s > %s > %s). Try again"

# validate create new listing data
CREATE_LISTING_RETAIL_PRICE_LESS_THAN_1 = u'Retail price must be greater than £1'
CREATE_LISTING_RETAIL_PRICE_LESS_THAN_SELLING_PRICE = "Retail price must be greater than selling price"
CREATE_LISTING_TOO_MANY_PHOTOS = 'You can add only 3 photos'