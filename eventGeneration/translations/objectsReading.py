import pandas as pd


def get_objects(filename):
    with open(filename, 'r') as f:
        for row_id, l in pd.read_csv(f).iterrows():
            yield l


def get_in_averages(timepoint, groups, every):
    return [
        i * every
        for i in range(int((timepoint - groups + every) / every), int(timepoint / every) + 1)
        if i >= 0
    ]


def split(filepath, groups, every):
    res = {}

    for l in get_objects(filepath):
        for t in get_in_averages(l[0], groups, every):
            if t in res:
                res[t] = res[t].append(l)
            else:
                res[t] = pd.DataFrame([l])

    return res


def group_by_class(to_average):
    return to_average.groupby('class')


def group_by_frame(to_average):
    return to_average.groupby('time')
