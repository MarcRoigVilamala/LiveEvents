import math

import click
import pandas as pd
from itertools import combinations

from objectsReading import split, group_by_frame

DEFAULT_OUTPUT_PATH = '/home/marc/projectes/TPLP-Data.v2012.11.10/interestFiltering/overlapping/'

WIDTH = 320  # Width of the image
HEIGHT = 240  # Height of the image
MAX_DIST = math.sqrt(WIDTH ** 2 + HEIGHT ** 2)  # Distance of the diagonal

BETA_COUNT = 5

OVERLAPPING_THRESHOLD = 0.85


class Pair(object):
    def __init__(self, obj1, obj2):
        if obj1 > obj2:
            self.obj1 = obj1
            self.obj2 = obj2
        else:
            self.obj1 = obj2
            self.obj2 = obj1

    def __hash__(self):
        return hash((self.obj1, self.obj2))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return '{0}, {1}'.format(self.obj1, self.obj2)


def get_combinations(objects):
    return combinations(map(lambda x: x[1], objects.iterrows()), 2)


def get_center(obj):
    return (
        (obj['x1'] + obj['x2']) / 2,
        (obj['y1'] + obj['y2']) / 2
    )


def get_distance(point_a, point_b):
    return math.sqrt((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2)


def count_beta(to_overlap, n_frames):
    def count_positives(pos):
        return 1 + sum(
            map(
                lambda x: x * BETA_COUNT,
                filter(
                    lambda x: x >= OVERLAPPING_THRESHOLD,
                    pos
                )
            )
        )  # Positives is the weighted sum of all the ones that are over the threshold

    def count_negatives(pos):
        return 1 + sum(
            map(
                lambda x: (1 - x) * BETA_COUNT,
                filter(
                    lambda x: x < OVERLAPPING_THRESHOLD,
                    pos
                )
            )
        )  # Negatives is the weighted sum of all the ones that are below the threshold

    def calculate_beta(positives_probs):
        pos = count_positives(positives_probs)
        neg = count_negatives(positives_probs)

        return pos / (pos + neg)

    probs = {}

    for frame, objects in group_by_frame(to_overlap):

        for object_a, object_b in get_combinations(objects):
            dist = get_distance(get_center(object_a), get_center(object_b))

            prob = 1 - dist / MAX_DIST

            key = Pair(
                object_a['class'].replace(' ', '_').lower(),
                object_b['class'].replace(' ', '_').lower()
            )

            probs.setdefault(key, dict())
            probs[key].setdefault(frame, list())

            probs[key][frame].append(prob)

    # return {
    #     key: min(
    #         [
    #             max(p)
    #             for p in d.values()
    #         ]
    #     )
    #     for key, d in probs.items()
    # }

    return {
        key: max(
            [
                max(p)
                for p in d.values()
            ]
        )
        for key, d in probs.items()
    }

    # return {
    #     key: max(positives)
    #     for key, positives in probs.items()
    # }


@click.command()
@click.argument('filename', required=True, type=click.Path(exists=True))
@click.argument('output_path', required=False, type=click.Path(), default=DEFAULT_OUTPUT_PATH)
def translate(filename, output_path, average_n_frames=16, every_n_frames=8):
    output_filename = filename.split('/')[-1].split('.')[0] + '.pl'

    with open(output_path + output_filename, 'w') as o:
        timepoints = set()

        for timepoint, to_overlap in split(filename, average_n_frames, every_n_frames).items():
            timepoints.add(int(timepoint))

            overlaps = count_beta(to_overlap, average_n_frames)

            for key, probability in overlaps.items():
                if probability > OVERLAPPING_THRESHOLD:
                    o.write(
                        "{0}::happensAt(overlapping({1}), {2}).\n".format(
                            probability, key, timepoint
                        )
                    )

        # o.write('allTimePoints({0}).\n'.format(sorted(list(timepoints))))


if __name__ == '__main__':
    translate()
