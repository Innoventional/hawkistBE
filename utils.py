def pick(d, *a):
    """
    Return a copy of the object, filtered to only have values for the whitelisted keys (or array of valid keys).

    >>> pick({'foo': 1, 'bar': 2}, 'foo')
    {'foo': 1}

    >>> pick({'foo': 1, 'bar': 2}, 'foo', 'bar')
    {'foo': 1, 'bar': 2}

    >>> pick({'foo': 1, 'bar': 2}, 'foo', 'bar', 'baz')
    {'foo': 1, 'bar': 2}

    >>> pick({'foo': 1, 'bar': 2}, 'baz')
    {}

    >>> pick({'foo': 1, 'bar': 2})
    {}
    """
    assert isinstance(d, dict)
    a = set(a)
    return dict(filter(lambda x: x[0] in a, d.items()))


def pluck(d, prop):
    """
    A convenient version of what is perhaps the most common use-case for map: extracting a list of property values.

    >>> pluck([{'name': 'moe', 'age': 40}, {'name': 'larry', 'age': 50}, {'name': 'curly', 'age': 60}], 'name')
    ['moe', 'larry', 'curly']
    """
    return map(lambda x: x.get(prop), d)


def defaults(d, _def):
    """
    Fill in null and undefined properties in object with values from the defaults objects, and return the object.
    As soon as the property is filled, further defaults will have no effect.

    >>> defaults({1: 1}, {1: 2})
    {1: 1}

    >>> defaults({1: 1}, {2: 2})
    {1: 1, 2: 2}

    >>> defaults({1: {11: 11}}, {1: {22: 22}})
    {1: {11: 11, 22: 22}}

    >>> defaults({1: None}, {1: {22: 22}})
    {1: None}
    """
    d = dict(x for x in d.items())
    for k, v in _def.items():
        if k not in d:
            d[k] = v
        elif isinstance(v, dict) and d[k] is not None:
            d[k] = defaults(d[k], v)
    return d


if __name__ == '__main__':
    import doctest
    doctest.testmod()

def get_object_or_none(cls_or_qs, *a, **kw):
    if isinstance(cls_or_qs, QuerySet):
        objs = cls_or_qs
    elif isinstance(cls_or_qs, type(Model)):
        objs = cls_or_qs.objects.all()
    else:
        objs = cls_or_qs.all()
    for o in objs.filter(*a, **kw):
        return o
    return