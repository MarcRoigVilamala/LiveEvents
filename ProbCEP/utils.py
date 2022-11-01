from itertools import groupby


def unsorted_groupby(iterable, key=None):
    return groupby(sorted(iterable, key=key), key=key)


def term_to_list(term):
    if term.args:
        return [term.args[0].value] + term_to_list(term.args[1])
    else:
        return []


def get_event_values(term):
    gen_event = term.args[0].args[0]

    event = gen_event.functor
    ids = gen_event.args
    timestamp = term.args[1].value

    return event, ids, timestamp


def get_values(aux):
    term = aux[0]
    prob = aux[1]

    event, ids, timestamp = get_event_values(term)

    return event, ids, timestamp, prob
