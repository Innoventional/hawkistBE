HAWKIST
==============

Server setup:

You should have postgresql, pip, virtualenv installed.

1. Init virtualenv: cd to your project root and type 'virtualenv .env'
2. Activate virtualenv: . .env/bin/activate
3. Install packages: pip install -r requirements.txt
4. Create user for db: createuser hawkist -dSR
5. Create db: createdb hawkist -U hawkist
6. Upgrade from alembic: alembic upgrade head
    

REST API
--------------------------

Basic auth:

    Key: c7f3380a074f4736
    Pass: 8ec1d0c900079d0a
    
Test request: 

    url: 'http://45.55.197.87:8003/api/test'
    type: 'GET'

Response:

    Headers:
        ...
        Content-Type: application/json; charset=UTF-8

    Data:
        {
            "info": "Hawkist API server", 
            "server_date": "2015-06-03T15:44:59.687933"
        }


--------------------------
### User registration

UserType

    Admin = 0
    Developer = 1
    Support = 2
    Standard = 3
        
        
        
SystemStatus

    Active = 0
    Suspended = 1
    
    
    
USER_INFO_DICT
    
    {
        'id': ID,
        'avatar': AVATAR URL or None,
        'thumbnail': THUMBNAIL URL or None,
        'username': USERNAME,
        'email': USERNAME,
        'about_me': INFO ABOUT USER or None,
        'phone': MOBILE NUMBER or None,
        'facebook_id': FACEBOOK ID or None,
        'email_status': EMAIL CONFIRMATION STATUS,
        'first_login': DOES THIS USER LOGIN FIRST FLAG,
        'metatags': LIST OF USER TAGS,
        'user_type': ACCOUNT TYPE,
        'system_status': SYSTEM STATUS,
        'city': LOCATION CITY or None,
        'last_activity': LAST USER ACTIVITY TIME,
        'number_of_sales': NUMBER OF LISTING SALES,
        'rating': RATING VALUE,
        'review': REVIEW NUMBER,
        'response_time': AVERAGE USER RESPONSE TIME
    }



**Registration**

    Url: 'users'
    Method: 'POST'
    Content-Type: application/json; charset=UTF-8

Data:

    {
        [<phone> or <facebook_token> ] : string
    }
    

Response Success:
    
    {
        'status': 0,
        'user': USER_INFO_DICT
    }
    
    USER_INFO_DICT:
    
    {
        "username": "",
        "email": "",
        "about_me": "",
        "avatar": "",
        "phone": "380993351739",
        "email_status": true,
        "facebook_id": "",
        "id": 1,
        "thumbnail": ""
    }

Response Failure:

    {
        'status': 1 / 2,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }



**Login (for phone)**

    Url: 'users'
    Method: 'PUT'
    Content-Type: application/json; charset=UTF-8
    
Data:

    {
        [<phone, pin>] : string
    }

Response Success:
    
    {
        'status': 0,
        'user': USER_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1 / 3 / 4 / 5,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    

    
**Logout**

    Url: 'user/logout'
    Method: 'PUT'
    Content-Type: application/json; charset=UTF-8
    
Data:

    {
        
    }

Response:

    { 
        'status': 0
    }
    
    
--------------------------
### User profile

**Your profile**

    Url: 'user'
    Method: 'GET'

Response:

    {
        "status": 0,
        "user": USER_INFO_DICT
    }
    


**Update username / email / about me / avatar**

    Url: 'user'
    Method: 'POST'


Data:

    {
        [<username> | <email> | <about_me> ] : string
    }
    
    + image in files

Response Success:
    
    {
        'status': 0,
        'user': USER_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    

    
**Link facebook to profile**

    Url: 'user/socials'
    Method: 'PUT'


Data:

    {
        "facebook_token" : "YOUR_FACEBOOK_ACCESS_TOKEN"
    }

Response Success:
    
    {
        'status': 0,
        'user': USER_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }


--------------------------
### Tags
    
**Get the list of all tags**

    Url: 'metatags'
    Method: 'GET'

Response:

    {
        "status": 0,
        "tags": [
            {
                "id": 1,
                "parent_tag_id": "",
                "name": "Console"
            },
            {
                "id": 2,
                "parent_tag_id": 1,
                "name": "PS3"
            }
        ]
    }



**Add tags to feed**

    Url: 'user/metatags'
    Method: 'PUT'


Data:

    {
        "tags": [
            {
                "type": VALID_TAG_TYPE,         - int      
                "id": int
            }, 
            .
            .
            .
            {
                "type": VALID_TAG_TYPE, 
                "id": int
            }
        ]
    }
    
    
VALID_TAG_TYPE

    Platform = 0
    Category = 1
    Subcategory = 2


Response Success:
    
    {
        'status': 0,
        'user': USER_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    


**Feeds to short (get available platforms)**

    Url: 'user/metatags'
    Method: 'GET'


Response Success:
    
    {
        'status': 0,
        'tags': [
            {
                "parent_id": null,
                "id": ID,
                "name": TITLE OF PLATFORM
            },
            .
            .
            .
            {
                ...
            }
        ]
    }
    

--------------------------
### Another users

**Get all users in application**
    
    url = '/users'
    type: 'GET'
    
Response:
    
    {
        "status": 0,
        "users": [
            {
                ...
            },
            {
                ...
            }
        ]
    }
    


Get user by id:

    url = '/user?id=USER_ID'
    type: 'GET'

Response:

    {
        "status": 0,
        "user": {
            USER_INFO_DICT,
            'follow': DOES THIS USER FOLLOW YOU FLAG,
            'following': DO YOU FOLLOW THIS USER FLAG
            'blocked' : DO YOU BLOCK THIS USER
        }
    }
    


**Search user by username / email**
    
    url = '/users?q=a'
    type: 'GET'
    
Response:
    
    {
        "status": 0,
        "users": [
            {
                ...
            },
            {
                ...
            }
        ]
    }
    

--------------------------
### Following
   
**Get my followers**

    Url: 'user/followers'
    Method: 'GET'
    
Response:
    
    {
        "status": 0,
        "users": [
            {
                ...
            },
                .
                .
                .
            {
                ...
            }
        ]
    }
    


**Get another user followers**

    Url: 'user/followers?user_id=USER_ID'
    Method: 'GET'
    
Response:
    
    {
        "status": 0,
        "users": [
            {
                ...
            },
                .
                .
                .
            {
                ...
            }
        ]
    }
    


**Get people I follow**

    Url: 'user/followers?following=true'
    Method: 'GET'
    
Response:
    
    {
        "status": 0,
        "users": [
            {
                ...
            },
                .
                .
                .
            {
                ...
            }
        ]
    }
    


**Get people which another user follow**

    Url: 'user/followers?following=true&user_id=USER_ID'
    Method: 'GET'
    
Response:
    
    {
        "status": 0,
        "users": [
            {
                ...
            },
                .
                .
                .
            {
                ...
            }
        ]
    }
    


**Follow someone**

    Url: 'user/followers'
    Method: 'POST'
    

Data:

    {
        "user_id": USER_TO_FOLLOW_ID,
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    } 



**Unfollow someone**

    Url: 'user/followers?user_id=USER_TO_UNFOLLOW_ID'
    Method: 'DELETE'
    

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    } 


--------------------------
### Block a user
   
**Block someone**

    Url: 'user/blocking'
    Method: 'POST'
    

Data:

    {
        "user_id": USER_TO_BLOCK_ID,
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    } 



**Unblock someone**

    Url: 'user/blocking?user_id=USER_TO_UNBLOCK_ID'
    Method: 'DELETE'

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    } 

 
--------------------------
### Items

ListingStatus

    Active = 0
    Reserved = 1
    Sold = 2
    
ITEM_INFO_DICT
    
    {
        'id': ID,
        'user_id': SELLER ID,
        'user_username': SELLER USERNAME,
        'user_avatar': SELLER AVATAR,
        'created_at': CREATED TIME,
        'title': TITLE,
        'description': DESCRIPTION,
        'platform': PLATFORM ID,
        'category': CATEGORY ID,
        'subcategory': SUBCATEGORY ID,
        'condition': CONDITION ID,
        'color': COLOUR ID,
        'retail_price': RETAIL PRICE,
        'selling_price': SELLING PRICE,
        'discount': DISCOUNT VALUE,
        'shipping_price': SHIPPING PRICE,
        'collection_only': COLLECTION ONLY FLAG,
        'post_code': POST CODE,
        'city': LOCATION CITY,
        'photos': LIST OF LISTING PHOTOS,
        'sold': IS LISTING ALREADY SOLD FLAG,
        'likes': NUMBERS OF LIKES,
        'liked': DOES CURRENT USER ALREADY LIKED THIS ITEM,
        'comments': NUMBER OF COMMENTS,
        'views': NUMBER OF VIEWS
    }
   
**Get all items (user feeds)**

    Url: 'listings'
    Method: 'GET'
    
Response:
    
    {
        "status": 0,
        "paginator": {
            "items_count": 103,
            "page": 1,
            "pages": 2
        },
        "items": [
            {
                ITEM_INFO_DICT
            },
                .
                .
                .
            {
                ITEM_INFO_DICT
            }
        ]
    }
    

   
**Get item by id**

    Url: 'listings?listing_id=ITEM_ID'
    Method: 'GET'
    
Response success:
    
    {   
        "status": 0,
        "item": [
            {
                ITEM_INFO_DICT
            }
        ],
        "similar_items": [
            {
                ITEM_INFO_DICT
            },
                .
                .
                .
            {
                ITEM_INFO_DICT
            }
        ],
        "user_items": [
            {
                ITEM_INFO_DICT
            },
                .
                .
                .
            {
                ITEM_INFO_DICT
            }
        ],
        
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
       
       
       
**Get item by user id**

    Url: 'listings?user_id=USER_ID'
    Method: 'GET'
    
Response success:
    
    {   
        "status": 0,
        "items": [
            {
                ITEM_INFO_DICT
            },
                .
                .
                .
            {
                ITEM_INFO_DICT
            }
        ]
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
      
**Search in items**

    Url: 'listings?q=SEARCHING_QUERY'
    Method: 'GET'
    
Response:
    
    {   
        "status": 0,
        "paginator": {
            ...
        },
        "items": [
            {
                ITEM_INFO_DICT
            },
                .
                .
                .
            {
                ITEM_INFO_DICT
            }
        ]
    }
    



**Check user selling ability**

    Url: 'check_selling_ability'
    Method: 'GET'


Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }    
   



**Create item**

    Url: 'listings'
    Method: 'POST'


Data:

    {
        "title": string,
        "description": string,
        "platform": int,            -- id, platform ex: XBOX
        "category": int,            -- id, category ex: Games
        "subcategory": int,         -- id, subcategory ex: Shooter
        "condition": int,
        "color": int,
        "retail_price": float,
        "selling_price": float,
        "shipping_price": float,
        "collection_only": int,
        "barcode": "http://amazon.link_to_barcode_photo",         - not required -
        "photos": ["http://amazon.link_to_photo"],
        "post_code": "NR1",
        "city": "Norwich"
    }

Response Success:
    
    {
        'status': 0,
        'item': ITEM_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1 / 6,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }    



**Update item**

    Url: 'listings'
    Method: 'POST'


Data:

    {
        "id": int,
        "title": string,
        "description": string,
        "platform": int,            -- id, platform ex: XBOX
        "category": int,            -- id, category ex: Games
        "subcategory": int,         -- id, subcategory ex: Shooter
        "condition": int,
        "color": int,
        "retail_price": float,
        "selling_price": float,
        "shipping_price": float,
        "collection_only": int,
        "barcode": "http://amazon.link_to_barcode_photo",         - not required -
        "photos": ["http://amazon.link_to_photo"],
        "post_code": "NR1",
        "city": "Norwich"
    }

Response Success:
    
    {
        'status': 0,
        'item': ITEM_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1 / 6,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }


   
**Delete item**

    Url: 'listings'
    Method: 'DELETE'


Data:

    {
        "listing_id": int
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': ERROR_STATUS_CODE,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    

   
   
**Like/dislike item**

    Url: 'listings/likes/LISTING_ID'
    Method: 'PUT'

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': ERROR_STATUS_CODE,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }




**Get wishlist (list of liked listings)**

    Url: 'user/wishlist'
    Method: 'GET'

Response Success:
    
    {
        'status': 0,
        'items': [
            {
                ITEM_RESPONSE_DICT
            }
        ]
    }
    


**Get wishlist (list of liked listings) by user id**

    Url: 'user/wishlist?user_id=USER_ID'
    Method: 'GET'

Response Success:
    
    {
        'status': 0,
        'items': [
            {
                ITEM_RESPONSE_DICT
            }
        ]
    }
    
    
    
**Get city by post code**

    Url: 'get_city'
    Method: 'PUT'


Data:

    {
        "post_code": string
    }

Response Success:
    
    {
        'status': 0,
        'city': CITY_NAME
    }
    
Response Failure:

    {
        'status': 7 / 8,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    

--------------------------
### Comments

COMMENT_RESPONSE_DICT

    {
        "id": ID,
        "created_at": CREATED NAME,
        "user_id": CREATER ID,
        "user_username": CREATER USERNAME,
        "user_avatar": CREATER AVATAR,
        "listing_id": COMMENTED LISTING ID,
        "text": TEXT,
        "offer": {
            "id": ID,
            "status": 0 IF THIS OFFER IS UNANSWERED,
            "offer_creater_id": USER WHO CREATE OFFER ID,
            "offer_receiver_id": OFFERED LISTING OWNER ID
        },
        "offer_id": OFFER ID OR NONE,
        "mentions": [
            {
                "id": MENTIONED USER ID,
                "username": MENTIONED USER USERNAME
            },
            .
            .
            .
            {
                ...
            }
        ]
    }
   
**Get all comments by current item**

    Url: 'listings/comments/LISTING_ID'
    Method: 'GET'
    
Response:
    
    {
        "status": 0,
        "comments": [
            {
                COMMENT_RESPONSE_DICT
            },
            .
            .
            .
            {
                COMMENT_RESPONSE_DICT
            }
        ]
    }



**Create new comment**

    Url: 'listings/comments/LISTING_ID'
    Method: 'POST'


Data:

    {
        "text": str,
        "image_url": str
    }

Response Success:
    
    {
        'status': 0,
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    
**Get people to mention in comment**

    Url: 'listings/comments_people?q=SEARCHING_QUERY'
    Method: 'GET'


Response:
    
    {
        'status': 0,
        'users': [
            {
                'id': ID,
                'username': USERNAME
            }, 
            .
            .
            .
            {
                ...
            }
        ]
    }
    

--------------------------
### Offers

**Offer a new price**

    Url: 'listings/offers/LISTING_ID'
    Method: 'POST'


Data:

    {
        "new_price": float
    }

Response Success:
    
    {
        'status': 0,
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }



**Accept an offer**

    Url: 'listings/offers/OFFER_ID'
    Method: 'PUT'


Data:

    {
        "new_status": 1
    }

Response Success:
    
    {
        'status': 0,
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    
**Decline an offer**

    Url: 'listings/offers/OFFER_ID'
    Method: 'PUT'


Data:

    {
        "new_status": 2
    }

Response Success:
    
    {
        'status': 0,
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    

--------------------------
### Stripe

CARD_INFO_DICT
    
    "id": STRIPE CARD ID,
    "name": CARDHOLDER NAME,
    "last4": LAST 4 NUMBER OF CARD,
    "address_line1": ADDRESS LINE 1,
    "address_line2": ADDRESS LINE 2,
    "city": ADDRESS CITY,
    "postcode": ADDRESS POST CODE,
    "exp_month": MONTH OF CARD EXPIRATION,
    "exp_year": YEAR OF CARD EXPIRATION



**Get all bank cards**

    Url: 'user/cards'
    Method: 'GET'



Response:
    
    {
        'status': 0,
        'cards': [
            {
                CARD_INFO_DICT
            },
            {
                ...
            },
            {
                CARD_INFO_DICT
            }
        ],
        'balance': 12.75
    }

    
    
**Add new bank card**

    Url: 'user/cards'
    Method: 'POST'


Data:

    {
        "stripe_token": STRIPE TOKEN
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }



**Update card**

    Url: 'user/cards'
    Method: 'PUT'


Data:

    {
        'id': STRIPE CARD ID,
        'name': CARDHOLDER NAME,
        'city': CARD CITY,
        'postcode': CARD POSTCODE,
        'address_line1': ADDRESS LINE 1,
        'address_line2': ADDRESS LINE 2,
        'exp_month': EXPIRATION CARD MONTH,
        'exp_year': EXPIRATION CARD YEAR
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }



**Delete card**

    Url: 'user/cards?card_id=CARD_TO_DELETE_ID'
    Method: 'DELETE'


Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    
--------------------------
### My orders

ORDER_INFO_DICT

    "id": USER ORDER ID,
    "status": ORDER STATUS,
    "listing": LISTING_INFO_DICT,
    "available_feedback": IS FEEDBACK AVAILABLE VALUE

ORDER STATUSES
    
    Active = 0
    Received = 1
    HasAnIssue = 2
    
ORDER ISSUE REASONS
    
    ItemHasNotArrived = 0
    ItemIsNotAsDescribed = 1
    ItemIsBrokenOrNotUsable = 2

    
**Get my orders list**

    Url: 'user/orders'
    Method: 'GET'


Response :
    
    {
        'status': 0,
        'orders': [
            {
                ORDER_INFO_DICT
            },
            {
                ...
            },
            {
                ORDER_INFO_DICT
            }
        ]
    }
    
    
**Search in orders (by listing title and platform name)**

    Url: 'user/orders?q=SEARCHING_QUERY'
    Method: 'GET'


Response :
    
    {
        'status': 0,
        'orders': [
            {
                ORDER_INFO_DICT
            },
            {
                ...
            },
            {
                ORDER_INFO_DICT
            }
        ]
    }
    
    
**Buy item (create stripe charge)**

    Url: 'user/orders'
    Method: 'POST'


Data:

    {
        "stripe_card_id": STRIPE CARD ID,
        "listing_id": LISTING ID
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }   
    
    
**Order received**

    Url: 'user/orders'
    Method: 'PUT'


Data:

    {
        "order_id": USER ORDER ID,
        "new_status": 1
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
       
    
**Orders has in issue**

    Url: 'user/orders'
    Method: 'PUT'


Data:

    {
        "order_id": USER ORDER ID,
        "new_status": 2,
        "issue_reason": ISSUE REASON ID
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }
    
--------------------------
### Addresses

ADDRESS_INFO_DICT

    "id": USER ADDRESS ID,
    "address_line1": ADDRESS LINE 1,
    "address_line2": ADDRESS LINE 2,
    "city": CITY,
    "postcode": POSTCODE
    
    
**Get my addresses list**

    Url: 'user/addresses'
    Method: 'GET'


Response :
    
    {
        'status': 0,
        'addresses': [
            {
                ADDRESS_INFO_DICT
            },
            {
                ...
            },
            {
                ADDRESS_INFO_DICT
            }
        ]
    }
    
    
**Add new address**

    Url: 'user/addresses'
    Method: 'POST'


Data:

    {
        "address_line1": ADDRESS LINE 1,            - required
        "address_line2": ADDRESS LINE 2,           
        "city": CITY,                               - required           
        "postcode": POSTCODE                        - required           
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }   
    

**Get recently added card address info**

    Url: 'user/addresses'
    Method: 'PUT'


Response Success:
    
    {
        'status': 0,
        'addresses': {
            "address_line1": ADDRESS LINE 1,
            "address_line2": ADDRESS LINE 2,
            "city": CITY,
            "postcode": POSTCODE
        }
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }   
       
    
**Update address**

    Url: 'user/addresses'
    Method: 'POST'


Data:

    {
        "id": ADDRESS ID,                           - required
        "address_line1": ADDRESS LINE 1,            - required
        "address_line2": ADDRESS LINE 2,           
        "city": CITY,                               - required           
        "postcode": POSTCODE                        - required           
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }   
    

**Delete address**

    Url: 'user/addresses?address_id=ADDRESS_TO_DELETE_ID'
    Method: 'DELETE'


Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }   
    
    
--------------------------
### Feedbacks

FEEDBACK_INFO_DICT

    "id": FEEDBACK ID,
    "text": FEEDBACK TEXT,
    "type": FEEDBACK_TYPE,
    "created_at": FEEDBACK CREATED TIME,
    "user": {
        "id": USER WHO LEAVE FEEDBACK ID,
        "username": USER USERNAME,
        "avatar": USER AVATAR
    }
    
FeedbackType

    Positive = 0
    Negative = 1
    Neutral = 2
    
    
**Get user feedbacks**

    Url: 'user/feedbacks/USER_ID'
    Method: 'GET'


Response :
    
    {
        'status': 0,
        "feedbacks": {
            "positive": [],
            "neutral": [],
            "negative": [{
                FEEDBACK_INFO_DICT
            }]
        }
    }
    
    
**Add new feedback**

    Url: 'user/feedbacks/USER_ID'
    Method: 'POST'


Data:

    {
        "order_id": ORDER TO CREATE FEEDBACK ID,
        "text": FEEDBACK TEXT,
        "type": FEEDBACK TYPE
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }  
     
--------------------------
### User Balance

    
**Get user balance**

    Url: 'user/banking/wallet'
    Method: 'GET'


Response :
    
    {
        "status": 0,
        "balance": {
            "available": "25.00",
            "pending": "0.00"
        }
    }
    
**Get user info**

    Url: 'user/banking/user_info'
    Method: 'GET'


Response :
    
    {
        "status": 0,
        "user_info": {
            "first_name": USER FIRST NAME,
            "last_name": USER LAST NAME,
            "birth_date": USER BIRTH DATE,
            "birth_month": USER BIRTH MONTH,
            "birth_year": USER BIRTH YEAR
        }
    }
    

**Update user info**

    Url: 'user/banking/user_info'
    Method: 'PUT'


Data:

    {
        "first_name": str,
        "last_name": str,
        "birth_date": str,
        "birth_month": str,
        "birth_year": str
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }  
    
**Get bank account info**

    Url: 'user/banking/account'
    Method: 'GET'


Response :
    
    {
        "status": 0,
        "account": {
            "holder_first_name": BANK ACCOUNT HOLDER FIRST NAME,
            "holder_last_name": BANK ACCOUNT HOLDER LAST NAME,
            "number": BANK ACCOUNT NUMBER,
            "sort_code": BANK ACCOUNT SORT CODE
        }
    }
    

**Update bank account info**

    Url: 'user/banking/account'
    Method: 'PUT'


Data:

    {
        "holder_first_name": str,
        "holder_last_name": str,
        "number": str,
        "sort_code": str
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    }  
       
       
**Get bank account address**

    Url: 'user/banking/address'
    Method: 'GET'


Response :
    
    {
        "status": 0,
        "address": {
            "address_line1": ADDRESS LINE 1,
            "address_line2": ADDRESS LINE 2 OR NULL,
            "city": CITY,
            "post_code": POST CODE
        }
    }
    

**Update bank account address**

    Url: 'user/banking/address'
    Method: 'PUT'


Data:

    {
        "address_line1": str,
        "address_line2": str,
        "city": str,
        "post_code": str
    }

Response Success:
    
    {
        'status': 0
    }
    
Response Failure:

    {
        'status': 1,
        'message': '',          — Error message text
        'title': ''          — Error message title 
    } 
     

STATUS CODES FOR CUSTOM ERROR TITLE
-----------------------------------
    
    Status code | Error message title
    ---------------------------------
        2       | No bank card
        403     | Access denied
    