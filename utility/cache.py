import memcache


class Cache(object):
    _client = memcache.Client(['127.0.0.1:11211'], 0)

    @staticmethod
    def get_key(key):
        return 'com.sme.api.' + key

    @classmethod
    def read(cls, key, default=None):
        key = cls.get_key(key)
        v = cls._client.get(key)
        if v is None:
            v = default
        return v

    @classmethod
    def write(cls, key, value):
        key = cls.get_key(key)
        cls._client.set(key, value)
