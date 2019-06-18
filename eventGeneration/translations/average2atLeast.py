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
    output_filename = filename.split('/')[-1].split('.')[0] + '.pl'

    with open(output_path + output_filename, 'w') as o:
        timepoints = set()

        for timestamp, class_name, appearances, probability in get_objects(filename):
            timepoints.add(int(timestamp))

            o.write("{0}::happensAt(atLeast({1}, {2}), {3}).\n".format(
                probability, appearances, class_name.replace(' ', '_').lower(), timestamp)
            )

        # o.write('allTimePoints({0}).\n'.format(sorted(list(timepoints))))


if __name__ == '__main__':
    translate()
