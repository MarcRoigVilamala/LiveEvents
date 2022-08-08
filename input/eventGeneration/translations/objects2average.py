import csv
from functools import reduce
from itertools import combinations

import click

from input.eventGeneration.translations.objectsReading import split_objects, group_by_class, group_by_frame

BETA_COUNT = 5


def get_probabilities(to_average):
    res = {}
    max_count = {}

    for class_name, group in group_by_class(to_average):
        res[class_name] = {}
        max_count[class_name] = 0

        for frame, objects in group_by_frame(group):
            res[class_name][frame] = objects['score']

            max_count[class_name] = max(max_count[class_name], len(objects))

    return res, max_count


def multiply(to_multiply):
    return reduce(lambda x, y: x * y, to_multiply)


def count_average(to_average):
    prob, max_count = get_probabilities(to_average)

    res = {}

    for class_name, frames in prob.items():
        res[class_name] = {}
        for i in range(1, max_count[class_name] + 1):
            for frame, probabilities in frames.items():
                num_objects = len(probabilities)

                res[class_name][i][frame] = sum(
                    [
                        multiply(
                            map(
                                lambda x: probabilities[x] if x in comb else 1 - probabilities[x],
                                range(num_objects)
                            )
                        )
                        for comb in combinations(range(num_objects), i)
                    ]
                )

    return res


def count_beta(to_average, timestamp, n_frames):
    prob, max_count = get_probabilities(to_average)

    res = {}

    for class_name, frames in prob.items():
        res[class_name] = {}

        # probs_ex_by_frame will contain the probabilities of having exactly 0 to i - 1 objects for every frame
        probs_ex_by_frame = {}
        for i in range(1, max_count[class_name] + 1):
            positives = 1.0
            negatives = 1.0

            for frame in range(timestamp, timestamp + n_frames):
                probs_ex_by_frame.setdefault(frame, [])

                probabilities = list(frames.get(frame, []))
                num_objects = len(probabilities)

                if num_objects >= i:
                    # Calculate the probability of having exactly i - 1 objects in the frame
                    probs_ex_by_frame[frame].append(
                        sum(
                            [
                                multiply(
                                    [
                                        probabilities[obj] if obj in comb else 1 - probabilities[obj]
                                        for obj in range(num_objects)
                                    ]
                                )
                                for comb in combinations(range(num_objects), i - 1)
                            ]
                        )
                    )

                    # Probability of having at least i is 1 - (sum of having exactly every number between 0 and i - 1)
                    prob = 1 - sum(probs_ex_by_frame[frame])

                    positives += BETA_COUNT * prob
                    negatives += BETA_COUNT * (1 - prob)
                else:
                    negatives += BETA_COUNT

            res[class_name][i] = positives / (positives + negatives)

    return res


def save_average(output, average):
    with open(output, 'w') as o:
        writer = csv.writer(o)

        writer.writerow(
            ['Timestamp', 'Class', '# Appearances', 'Probability']
        )

        for timestamp in sorted(average.keys()):
            for class_name in average[timestamp]:
                for appearances in average[timestamp][class_name]:
                    writer.writerow(
                        [timestamp, class_name, appearances, average[timestamp][class_name][appearances]]
                    )


@click.command()
@click.argument('filepath', required=False, default='output.csv')
@click.argument('output', required=False, default='averages/output.csv')
def calculate_average(filepath='output.csv', output='averages/output.csv', average_n_frames=16, every_n_frames=8):
    res = {}

    for timestamp, to_average in split_objects(filepath, average_n_frames, every_n_frames).items():
        res[timestamp] = count_beta(to_average, timestamp, average_n_frames)

        print(timestamp, end="\r", flush=True)

    save_average(output, res)


if __name__ == '__main__':
    calculate_average()
