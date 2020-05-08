from collections import OrderedDict

def qsdict(qs, *args):
    """
    Convert a query string to a nested dict
    :param qs: The query string from which the array will be created. qs can also be an object and args are all attributes on that object.
    :param args: A list of fields which will be nested one inside the other in the dict. The last arg will be the value in the innermost dict. If an arg is callable then it will be executed with q as a parameter. If the last parameter is a tuple then all the values inside that tuple will be added as leaves.
    :return:  A nested dict

    e.g.
    qs = Queryset([{fa:1, fb:2, fc:3}, {fa:3, fb:4, fc:5}]),
    using fc as the value

    {
        1 : {
            2 : 3
        },
        3 : {
            4 : 5
        }
    }
    """

    if len(args) < 2:
        raise ValueError("Need at least two fields to nest dicts")

    def v(q, key):
        if callable(key):
            return key(q)
        elif type(key) == int and key in q:
            return q[key]
        elif hasattr(q, key):
            return getattr(q, key)
        elif key in q:
            return q[key]
        else:
            return None

    d = {}
    for q in qs:
        nested_dicts = [d]
        for key in args[:-2]:
            current_dict = nested_dicts[-1]
            value = v(q, key)
            if not value in current_dict:
                current_dict[value] = OrderedDict()
            nested_dicts.append(current_dict[value])
        current_dict = nested_dicts[-1]
        if type(args[-1]) == tuple:
            current_dict[v(q, args[-2])] = [v(q, el) for el in args[-1]]
        else:
            current_dict[v(q, args[-2])] = v(q, args[-1])

    return d

