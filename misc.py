

identity = lambda _: _



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



if __name__ == '__main__':
    print regularize_args(None, identity, int, int)('n a 2 3'.split())



