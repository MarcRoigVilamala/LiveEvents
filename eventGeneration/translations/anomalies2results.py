import click
import pandas as pd

DEFAULT_OUTPUT_PATH = '/home/marc/projectes/TPLP-Data.v2012.11.10/interestFiltering/atLeast/'


def get_objects(filename):
    with open(filename, 'r') as f:
        for l in pd.read_csv(f).iterrows():
            yield l[1]


@click.command()
@click.argument('filename', required=True, type=click.Path(exists=True))
@click.argument('output_path', required=False, type=click.Path(), default=DEFAULT_OUTPUT_PATH)
def translate(filename, output_path):
    with open(filename, 'r') as f:
        for l in f:
            video_filename, video_type, first_start, first_end, second_start, second_end = l.strip().split(' ')

            sequences = []

            if first_start != -1:
                sequences.append((first_start, first_end))
            if second_start != -1:
                sequences.append((second_start, second_end))




    output_filename = filename.split('/')[-1].split('.')[0] + '.pl'

    with open(output_path + output_filename, 'w') as o:
        timestamps = set()

        for timestamp, class_name, appearances, probability in get_objects(filename):
            timestamps.add(int(timestamp))

            o.write("{0}::happensAt(atLeast({1}, {2}), {3}).\n".format(
                probability, appearances, class_name.replace(' ', '_').lower(), timestamp)
            )

        # o.write('allTimeStamps({0}).\n'.format(sorted(list(timestamps))))


if __name__ == '__main__':
    translate()
