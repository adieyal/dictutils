def mergedict(a, b, path=None, update=True):
    """
    Derived from: http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
    merges b into a

        concatenate_arrays - if True then arrays are concatenate, otherwise they are recursively traversed 
        update - if True then values in b clobber values in a
    """
    if type(a) != dict or type(b) != dict:
        raise TypeError("Both a an b arguments must be dicts")

    if a == None and b == None:
        return None
    elif a == None:
        return b
    elif b == None:
        return a

    if len(b) == 0:
        return a
    elif len(a) == 0:
        return b


    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                mergedict(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key].extend(b[key])
            elif update:
                a[key] = b[key]
            else:
                pass
                #raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]

    return a
