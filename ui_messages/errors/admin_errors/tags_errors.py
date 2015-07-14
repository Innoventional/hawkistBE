__author__ = 'ne_luboff'

# in case if title of new platform/category/etc. is empty
# parameter - new tag type
ADMIN_TAG_EMPTY_TITLE = 'You must input new %s title'

# if admin user doesn't select parent tag
# parameter - parent tag type
ADMIN_TAG_EMPTY_PARENT = 'You must select %s'

# if not platform/category/etc.
# parameters - tag type and tag id
ADMIN_TAG_DOES_NOT_EXIST = 'No %s with id %s'

# for category type
ADMIN_CATEGORY_ALREADY_EXISTS = 'Category with name %s already exists in platform %s'
ADMIN_TRY_DELETE_CATEGORY_WHICH_IS_USED = 'Cannot delete the category tag %s (%s) because it is in use on an active ' \
                                          'listing. Please update the listing with another tag and try again.'

# for colour type
ADMIN_COLOUR_ALREADY_EXISTS = 'Color with name %s already exists in subcategory %s (%s > %s)'
ADMIN_TRY_DELETE_COLOUR_WHICH_IS_USED = 'Cannot delete the colour tag %s (%s > %s > %s) because it is in use on an ' \
                                        'active listing. Please update the listing with another tag and try again.'
 
# for conditiom type
ADMIN_CONDITION_ALREADY_EXISTS = 'Condition with name %s already exists in subcategory %s (%s > %s)'
ADMIN_TRY_DELETE_CONDITION_WHICH_IS_USED = 'Cannot delete the condition tag %s (%s > %s > %s) because it is in use on ' \
                                           'an active listing. Please update the listing with another tag and try again.'

# for platform type
ADMIN_PLATFORM_ALREADY_EXISTS = 'Platform with name %s already exists'
ADMIN_TRY_DELETE_PLATFORM_WHICH_IS_USED = 'Cannot delete the platform tag %s because it is in use on an active ' \
                                          'listing. Please update the listing with another tag and try again.'

# for subcategory type
ADMIN_SUBCATEGORY_ALREADY_EXISTS = 'Subcategory with name %s already exists in category %s (%s)'
ADMIN_TRY_DELETE_SUBCATEGORY_WHICH_IS_USED = 'Cannot delete the subcategory tag %s (%s > %s) because it is in use on ' \
                                             'an active listing. Please update the listing with another tag and try again.'
