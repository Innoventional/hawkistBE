import time
import jwt

__author__ = 'ne_luboff'

# jwt_secret = 'mzU2MTIc7gj1o6wQZgjNUbBRCNd8wdDAIhlydloq9A3BLG80'

# ZenDesk info@hawkist.com NinetyH5d1


def zendesk_create_jwt_token():
    payload = {
        "typ": "JWT",
        "alg": "HS256",
        "iat": time.time(),
        "jti": time.time(),
        "email": "gigek@mail.ru",
        "name": "Sergey_Borichev"
    }


    shared_key = "Izs6iWeheNemOLr6fVhDiRWAjhEQH0uCYJnUgVhA2GJe8ZT4"
    jwt_string = jwt.encode(payload, shared_key)

    url = 'https://hawkist.zendesk.com/access/jwt?jwt={0}'.format(jwt_string)
    return {
        'payload': payload,
        'payload_encoded': jwt_string,
        'url': url
    }

if __name__ == '__main__':
    print zendesk_create_jwt_token()
