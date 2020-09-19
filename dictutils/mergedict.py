from typing import Mapping, Dict, Optional, Iterable

def mergedict(*args, path=None, update=True):
    head, *tail = args

    for d in tail:
        head = _mergedict(head, d, path, update)  

    return head
    
def _mergedict(a: Dict, b: Dict, path=None, update: bool=True) -> Optional[Dict]:
    """
    Derived from: http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
    merges b into a

        concatenate_arrays - if True then arrays are concatenate, otherwise they are recursively traversed 
        update - if True then values in b clobber values in a
    """
    if not isinstance(a, Mapping) or not isinstance(b, Mapping):
        raise TypeError("Both a an b arguments must be dicts")

    if a == None and b == None:
        return None
    elif a == None:
        return b
    elif b == None:
        return a

    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _mergedict(a[key], b[key], path + [str(key)])
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
