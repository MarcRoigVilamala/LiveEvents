import json
import sys
import time

import matplotlib.pyplot as plt
import click
import numpy as np

from PyProbEC.cep import get_evaluation
from PyProbEC.model import Model
from PyProbEC.precompilation import PreCompilationArguments, Query
from eventGeneration.event import Event
from eventGeneration.eventGeneration import get_events
from videoFeed.videoFeed import VideoFeed


def update_evaluation(evaluation, new_evaluation):
    for event, event_val in new_evaluation.items():
        if event in evaluation:
            for ids, ids_val in event_val.items():
                if ids in evaluation[event]:
                    for timestamp, prob in ids_val.items():
                        evaluation[event][ids][timestamp] = prob
                else:
                    evaluation[event][ids] = ids_val
        else:
            evaluation[event] = event_val

    return evaluation


def update_graph(fig, ax, line1, evaluation, graph_x_size):
    x_data = sorted(evaluation['interesting']['()'].keys())
    y_data = [evaluation['interesting']['()'][k] for k in x_data]

    # print('x_data', x_data)
    # print('y_data', y_data)

    # Find which range we want to show based on the data we have
    max_data = x_data[-1]
    right = max(max_data, graph_x_size)
    left = right - graph_x_size

    # Increase the range by 10% on each side to make it less cramped
    left -= graph_x_size / 10
    right += graph_x_size / 10

    ax.set_xlim(left, right)

    line1.set_xdata(x_data)
    line1.set_ydata(y_data)
    fig.canvas.draw()
    fig.canvas.flush_events()


def at_rate(iterable, rate):
    period = 1.0 / rate

    start = time.time()

    for i, v in enumerate(iterable):
        now = time.time()
        to_wait = period * i - (now - start)
        if to_wait > 0:
            time.sleep(to_wait)

        yield v


@click.command()
@click.argument('expected_events')
@click.argument('event_definition')
@click.option('-w', '--max_window', default=32)
@click.option('--cep_frequency', default=8)
@click.option('-g', '--group_size', default=16)
@click.option('-f', '--group_frequency', default=8)
@click.option('--graph_x_size', default=100)
@click.option('-o', '--interesting_objects', default=None)
@click.option('--fps', default=30)
@click.option('--precompile', default=None)
def start_detecting(expected_events, event_definition, max_window, cep_frequency, group_size, group_frequency,
                    graph_x_size, interesting_objects, fps, precompile):
    if max_window < cep_frequency + group_frequency:
        print(
            'The window of events can not be smaller than the sum of the frequency of checking and grouping',
            file=sys.stderr
        )
        sys.exit(-1)

    with open(expected_events) as f:
        expected_events_list = [l.strip() for l in f]

    # Find which are the interesting objects
    if interesting_objects is None:
        interesting_objects_list = None
    else:
        with open(interesting_objects, 'r') as f:
            interesting_objects_list = [l.strip() for l in f]

    x = np.linspace(0, graph_x_size, graph_x_size)
    y = np.linspace(0, 1, graph_x_size)

    # You probably won't need this if you're embedding things in a tkinter plot...
    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(x, y, 'r-')  # Returns a tuple of line objects, thus the comma

    # for phase in np.linspace(0, 10*np.pi, 500):
    #     line1.set_ydata(np.sin(x + phase))
    #     fig.canvas.draw()
    #     fig.canvas.flush_events()

    video_input = VideoFeed()

    window = []
    events = []

    if precompile:
        with open(precompile, 'r') as f:
            aux = json.load(f)

        precomp_args = PreCompilationArguments(
            input_events=[Event(**e) for e in aux['input_events']],
            queries=[Query(**q) for q in aux['queries']]
        )

        model = Model([event_definition], precomp_args)
    else:
        model = Model([event_definition])

    evaluation = {}

    for i, frame in at_rate(enumerate(video_input), fps):
        # Keep only the number of frames we need
        window.append((i, frame))
        window = window[-group_size:]

        # Every group_frequency, get the relevant events
        if not (i + 1) % group_frequency:
            # print("Generating events at {} for {} to {}".format(i, i - group_size + 1, i))

            # Check that we have enough frames for the group (preventing errors on first iterations)
            if len(window) >= group_size:
                relevant_frames = window[-group_size:]

                events += get_events(relevant_frames, interesting_objects_list)

        # Every cep_frequency frames, run the CEP part with the relevant events
        # The i - max_window >= -1 is for the first iteration, where we do not have all the relevant frames
        if not (i + 1) % cep_frequency and i - group_size >= -1:
            # print("Executing problog at {} for {} to {}".format(i, i - max_window + 1, i))

            # Remove the events that happened before the current window
            while events and events[0].timestamp < i - max_window:
                # While we have events and the first event is before the current window, remove the first event
                events = events[1:]

            new_evaluation = model.get_probabilities_precompile(
                existing_timepoints=np.arange(0, i + 1, group_frequency),
                query_timepoints=[i - group_size + 1],
                expected_events=expected_events_list,
                input_events=events
            )

            events += Event.from_evaluation(new_evaluation)

            evaluation = update_evaluation(evaluation, new_evaluation)

            update_graph(fig, ax, line1, evaluation, graph_x_size)

            # time.sleep(1)

    print('################################################################################################')
    print(evaluation)


if __name__ == '__main__':
    start_detecting()
