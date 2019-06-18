import click

DEFAULT_OUTPUT_PATH = '/home/marc/projectes/TPLP-Data.v2012.11.10/interestFiltering/3DCN/'

THRESHOLD = 0.085


def get_labels(filename):
    with open(filename, 'r') as f:
        line = f.readline()

        while line:
            yield line.split(',', 1)

            line = f.readline()


@click.command()
@click.argument('filename', required=True, type=click.Path(exists=True))
@click.argument('output_path', required=False, type=click.Path(), default=DEFAULT_OUTPUT_PATH)
def translate(filename, output_path):
    output_filename = filename.split('/')[-1].split('.')[0] + '.pl'

    with open(output_path + output_filename, 'w') as o:
        timepoints = set()

        for timestamp, labels in get_labels(filename):
            timepoints.add(int(timestamp))

            # Remove end of line characters, initial "(( and end ))"
            labels = labels.strip()[3:-3]

            # Split the different labels
            for label in labels.split('), ('):
                probability, activity = label.split(', ')

                probability = float(probability)

                if probability > THRESHOLD:
                    o.write("{0}::happensAt(something, {1}).\n".format(probability, timestamp))
                else:
                    o.write("{0}::happensAt(nothing, {1}).\n".format(1 - probability, timestamp))

                break  # We only care about the first one

        o.write('allTimePoints({0}).\n'.format(sorted(list(timepoints))))


if __name__ == '__main__':
    translate()
