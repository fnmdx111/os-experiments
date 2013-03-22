# encoding: utf-8

identity = lambda _: _ # 一个占位函数，返回自己


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
    """规则化参数，未使用"""
    def _(args):
        result = []
        for arg, f in zip(args, r_args):
            if f:
                result.append(f(arg))
        return result
    return _


def take(iterable, by=8):
    """按by的步长取出iterable中的元素，例take([1, 2, 3, 4, 5, 6, 7], by=3) => [[1, 2, 3], [4, 5, 6], [7]]"""
    while iterable:
        if len(iterable) < by:
            yield iterable
        else:
            yield iterable[:by]
        iterable = iterable[by:]


def get_cmd(raw, fmt, hint=''):
    """按fmt从raw中取出对应位置的参数，并转换到对应类型，
    主要目的是抽象出命令的输入，减少代码的重复和混杂
    >>> get_cmd('r f 2 4 5', '%c %s &i', hint='proc_name pages')
    ['f', [2, 4, 5]]
    >>> get_cmd('d a', '%c %s', hint='proc_names')
    ['a']"""
    fmt = fmt.split()[1:] # `%c'是命令位，无实际用处，直接抛弃
    if len(raw) == 1 and fmt[0][0] != '&': # 如果仅输入了命令（即raw的长度为1）
        args = raw_input(hint + '> ').split()
    else:
        args = raw.split()[1:] # 取出命令的参数

    result = []
    while fmt:
        if fmt[0][0] == '&': # 如果当前的描述符是可变长度描述符`&'，
                             # 则可以认为已经达到最后一个参数了，
                             # 跳出while到后面单独处理
            break

        descriptor, type_ = fmt.pop(0) # 取出第一个描述符和类型
        arg = args.pop(0) # 取出对应位置的输入参数

        try:
            result.append(_type_dict[type_](arg))
        except BaseException:
            print 'incorrect argument, %s required' % _type_name_dict[type_]
            return None

    if fmt: # variable length argument
        _, type_ = fmt.pop(0) # 取出可变长度参数的类型
        try:
            result.append(map(_type_dict[type_], args))
        except BaseException:
            print 'incorrect argument, %s required' % _type_name_dict[type_]
            return None

    return result



if __name__ == '__main__':
    pass
    # print regularize_args(None, identity, int, int)('n a 2 3'.split())



