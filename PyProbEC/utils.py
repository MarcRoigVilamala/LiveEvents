from itertools import groupby


def unsorted_groupby(iterable, key=None):
    return groupby(sorted(iterable, key=key), key=key)


def term_to_list(term):
    if term.args:
        return [term.args[0].value] + term_to_list(term.args[1])
    else:
        return []


def get_values(aux):
    term = aux[0]
    prob = aux[1]

    gen_event = term.args[0].args[0]

    event = gen_event.functor
    ids = gen_event.args
    timepoint = term.args[1].value

    return event, ids, timepoint, prob
