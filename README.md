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

    Standard = 0
    Admin = 1
    Developer = 2
    Support = 3
        
class SystemStatus(Enum):

    Active = 0
    Suspended = 1

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
        'status': 1,
        'message': '' — Error message
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

Response:

    {...} - Full user info dict or 404 error if user was not found
    
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
        'message': '' — Error message
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
        'message': '' — Error message
    }
    
###Tags
    
**Get the list of all tags**

    Url: 'tags'
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

    Url: 'user/tags'
    Method: 'PUT'


Data:

    {
        "tags" : [1, 2]
    }


Response Success:
    
    {
        'status': 0,
        'user': USER_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1,
        'message': '' — Error message
    }
    
---
    
**Delete tags**

    Url: 'user/tags'
    Method: 'DELETE'


Data:

    {
        "tags" : [2]
    }


Response Success:
    
    {
        'status': 0,
        'user': USER_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1,
        'message': '' — Error message
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
        "user": {...}
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

### Items

   
**Create item**

    Url: 'user/items'
    Method: 'POST'


Data:

    {
        "title": string,
        "description": string,
        "platform": PLATFORM_VALUE,
        "category": CATEGORY_VALUE,
        "condition": CONDITION_VALUE,
        "color": [COLOR_VALUES],
        "retail_price": float,
        "selling_price": float,         - not required -
        "shipping_price": float,
        "collection_only": int,
        "barcode": "http://amazon.link_to_barcode_photo",         - not required -
        "photos": ["http://amazon.link_to_photo"]
    }

PLATFORM_VALUEs:

    PC = 0
    MAC = 1
    Playstation = 2
    XBOX = 3
    Nintendo = 4
    Sega = 5


CATEGORY_VALUEs:

    Consoles = 0
    Games = 1
    Handhelp = 2
    Accessories = 3

    
CONDITION_VALUEs:

    BrandNewInBox = 0
    LikeNew = 1
    Used = 2
    Refurbished = 3
    NotWorkingOrPartsOnly = 4


COLOR_VALUEs:

    Black = 0
    White = 1
    Red = 2
    Blue = 3
    Green = 4
    Orange = 5
    Yellow = 6
    Purple = 7
    Other = 8
    NotApplicable = 9


Response Success:
    
    {
        'status': 0,
        'item': ITEM_INFO_DICT
    }
    
Response Failure:

    {
        'status': 1,
        'message': '' — Error message
    }
    