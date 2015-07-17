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

###Used enum classes
    
class UserType(Enum):

    Admin = 0
    Developer = 1
    Support = 2
    Standard = 3
        
class SystemStatus(Enum):

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
    
###User registration

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
    
---

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
    
---
    
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
    

###User profile

**Your profile**

    Url: 'user'
    Method: 'GET'

Response:

    {
        "status": 0,
        "user": USER_INFO_DICT
    }
    
---

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
    
---
    
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
    
###Tags
    
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

---

**Add tags**

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
    
---
    
**Delete tags**

    Url: 'user/matatags'
    Method: 'DELETE'


Data:

    {
        "tags": [
            {
                "type": VALID_TAG_TYPE,         - int      
                "id": int
            }
        ]
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
    
---

###Another users

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
    
---

Get user by id:

    url = '/user?id=5'
    type: 'GET'

Response:

    {
        "status": 0,
        "user": {
            USER_INFO_DICT,
            'follow': DOES THIS USER FOLLOW YOU FLAG,
            'following': DO YOU FOLLOW THIS USER FLAG
        }
    }
    
---

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
    
---

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
    
---

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
    
---

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
---

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
---
 
### Items
   
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
    
---
   
**Get item by id**

    Url: 'listings?listing_id=ITEM_ID'
    Method: 'GET'
    
Response success:
    
    {   
        "status": 0,
        "item": [
            {
                ...
            }
        ],
        "similar_items": [
            {
                ...
            },
                .
                .
                .
            {
                ...
            }
        ],
        "user_items": [
            {
                ...
            },
                .
                .
                .
            {
                ...
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
    
---

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
    
---

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
    
---


STATUS CODES FOR CUSTOM ERROR TITLE
-----------------------------------
    
    Status code | Error message title
    ---------------------------------
        2       | Invalid Number Format
        3       | User Not Found
        4       | Wrong Pin
        5       | Cannot Sign In
        6       | (field_name) Missing
        7       | Incorrect Post Code
        8       | Post Code Not Found
    