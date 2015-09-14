import time
import jwt

__author__ = 'ne_luboff'

# ZenDesk info@hawkist.com NinetyH5d1

jwt_shared_key = 'Izs6iWeheNemOLr6fVhDiRWAjhEQH0uCYJnUgVhA2GJe8ZT4'


def zendesk_create_jwt(user_id, user_username, user_email):
    payload = {
        "typ": "JWT",
        "alg": "HS256",
        "iat": int(time.time() + user_id),
        "jti": "%.02f" % time.time(),
        "email": user_email,
        "name": user_username
    }

    jwt_string = jwt.encode(payload, jwt_shared_key)

    url = 'https://hawkist.zendesk.com/access/jwt?jwt={0}'.format(jwt_string)
    return {
        'payload': payload,
        'payload_encoded': jwt_string,
        'url': url
    }

if __name__ == '__main__':
    print zendesk_create_jwt(140, 'Sergey_Borichev', 'gigek@mail.ru')
