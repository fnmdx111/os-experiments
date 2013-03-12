

identity = lambda _: _


_type_dict = {
    'c': identity,
    's': str,
    'i': int
}

_type_name_dict ={
    'c': 'command',
    's': 'string',
    'i': 'integer'
}


def regularize_args(*r_args):
    def _(args):
        result = []
        for arg, f in zip(args, r_args):
            if f:
                result.append(f(arg))
        return result
    return _


def take(iterable, by=8):
    while iterable:
        if len(iterable) < by:
            yield iterable
        else:
            yield iterable[:by]
        iterable = iterable[by:]


def get_cmd(raw, fmt, hint=''):
    """get_cmd('r f 2 4 5', '%c %s &i', hint='proc_name pages')
       get_cmd('d a', '%c &s', hint='proc_names')"""
    fmt = fmt.split()[1:]
    if len(raw) == 1 and fmt[0][0] != '&': # only input cmd
        args = raw_input(hint + '> ').split()
    else:
        args = raw.split()[1:]

    result = []
    while fmt:
        if fmt[0][0] == '&':
            break

        descriptor, type_ = fmt.pop(0)
        arg = args.pop(0)

        try:
            result.append(_type_dict[type_](arg))
        except BaseException:
            print 'incorrect argument, %s required' % _type_name_dict[type_]
            return None

    if fmt: # variable length argument
        _, type_ = fmt.pop(0)
        try:
            result.append(map(_type_dict[type_], args))
        except BaseException:
            print 'incorrect argument, %s required' % _type_name_dict[type_]
            return None

    assert not fmt

    return result






if __name__ == '__main__':
    print get_cmd('r f 2 4 5', '%c %s &i', hint='proc_name pages')
    print get_cmd('r f ', '%c %s &i', hint='proc_name pages')
    print get_cmd('r', '%c %s &i', hint='proc_name pages')
    # print regularize_args(None, identity, int, int)('n a 2 3'.split())



