import json
import sys
import time

import cv2
import click
import numpy as np

from PyProbEC.model import Model
from preCompilation.PreCompilation import PreCompilationArguments
from PyProbEC.precompilation import EventQuery
from eventGeneration.event import Event
from eventGeneration.eventGeneration import EventGenerator
# from eventGeneration.objectDetection.objectDetection import ObjectDetectorEventGenerator
# from eventGeneration.hardCodedEvents import HardCodedObjectDetectorEventGenerator as ObjectDetectorEventGenerator
# from eventGeneration.hardCodedEvents import HardCodedVideoEventGenerator as VideoEventGenerator
from eventGeneration.fromFileEvents import FromFileEventGenerator
from graph import Graph
from videoFeed.videoFeed import VideoFeed

VIDEO_WINDOW_NAME = 'CCTV Feed'


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


def at_rate(iterable, rate):
    period = 1.0 / rate

    start = time.time()

    for i, v in enumerate(iterable):
        now = time.time()
        to_wait = period * i - (now - start)
        if to_wait > 0:
            time.sleep(to_wait)

        yield v


def generate_model(event_definition, precompile):
    if precompile:
        with open(precompile, 'r') as f:
            json_precompile = json.load(f)

        precomp_args = PreCompilationArguments(
            input_clauses=[Event(**e) for e in json_precompile['input_clauses']],
            queries=[EventQuery(**q) for q in json_precompile['queries']]
        )

        return Model([event_definition], precomp_args)
    else:
        return Model([event_definition])


def initialize_video(x, y):
    cv2.namedWindow(VIDEO_WINDOW_NAME)
    cv2.moveWindow(VIDEO_WINDOW_NAME, x, y)


def update_video(frame):
    cv2.imshow(VIDEO_WINDOW_NAME, frame)
    cv2.waitKey(1)


def start_detecting(expected_events, event_definition, max_window, cep_frequency, group_size, group_frequency,
                    graph_x_size, interesting_objects, fps, precompile, text, use_graph, video, video_name,
                    video_x_position, video_y_position):
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

    # If we are using a graph, create it
    if use_graph:
        graph = Graph(graph_x_size, expected_events_list)
    else:
        graph = None

    if video:
        initialize_video(video_x_position, video_y_position)

    video_input = VideoFeed(video_file='/home/marc/Videos/UCF_CRIME/Crime/Fighting/{}.mp4'.format(video_name))

    event_generator = EventGenerator(
        [
            # ObjectDetectorEventGenerator(interesting_objects_list),
            # VideoEventGenerator()
            FromFileEventGenerator('ProbLogEvents/Fighting/3DResNet/{}.pl'.format(video_name)),
            FromFileEventGenerator('ProbLogEvents/Fighting/AtLeast/{}.pl'.format(video_name)),
            FromFileEventGenerator('ProbLogEvents/Fighting/Overlapping/{}.pl'.format(video_name))
        ]
    )

    window = []
    events = []

    model = generate_model(event_definition, precompile)

    evaluation = {}

    for i, frame in at_rate(enumerate(video_input), fps):
        if video:
            update_video(frame)

        # Keep only the number of frames we need
        window.append((i, frame))
        window = window[-group_size:]

        # Every group_frequency, get the relevant events
        if not (i + 1) % group_frequency:
            # print("Generating events at {} for {} to {}".format(i, i - group_size + 1, i))

            # Check that we have enough frames for the group (preventing errors on first iterations)
            if len(window) >= group_size:
                relevant_frames = window[-group_size:]

                events += event_generator.get_events(relevant_frames)

        # Every cep_frequency frames, run the CEP part with the relevant events
        # The i - max_window >= -1 is for the first iteration, where we do not have all the relevant frames
        if not (i + 1) % cep_frequency and i - group_size >= -1:
            # print("Executing problog at {} for {} to {}".format(i, i - max_window + 1, i))

            # Remove the events that happened before the current window
            while events and events[0].timestamp < i - max_window:
                # While we have events and the first event is before the current window, remove the first event
                events = events[1:]

            new_evaluation = model.get_probabilities_precompile(
                existing_timestamps=np.arange(0, i + 1, group_frequency),
                query_timestamps=[i - group_size + 1],
                expected_events=expected_events_list,
                input_events=events
            )

            events += Event.from_evaluation(new_evaluation)

            evaluation = update_evaluation(evaluation, new_evaluation)

            if text:
                print(new_evaluation)

            if graph:
                graph.update(evaluation)

    print('################################################################################################')
    print(evaluation)

    if use_graph:
        input('Press enter to finish')

    cv2.destroyAllWindows()


@click.command()
@click.argument('expected_events', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument('event_definition', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option('-w', '--max_window', default=32, help='Maximum number of frames we want to remember')
@click.option('--cep_frequency', default=8, help='Frequency for calling the CEP code to generate new complex events')
@click.option('-g', '--group_size', default=16, help='Number of frames considered to generate each simple event')
@click.option('-f', '--group_frequency', default=8, help='Frequency with which we generate simple events')
@click.option('--graph_x_size', default=100, help='Size of the x axis (time) for the graph. Only if graph is in use')
@click.option(
    '-o', '--interesting_objects', default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='File defining the list of objects we care about from the object detector output'
)
@click.option('--fps', default=30, help='Number of frames that are processed every second')
@click.option(
    '--precompile', default=None, type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='JSON file defining the inputs and outputs for which we can use precompilation'
)
@click.option(
    '--text', is_flag=True, help='If used, a live text will be printed with the values of the different complex events'
)
@click.option(
    '--graph', is_flag=True,
    help='If used, a live graph will be generated showing the values of the different complex events'
)
@click.option('--video', is_flag=True, help='If used, a live video will be shown')
@click.option('--video_name', default=None, help='Name of the video for which we want to perform CEP')
@click.option('--video_x_position', default=1000, help='X position to spawn the video. Only if video is in use')
@click.option('--video_y_position', default=200, help='Y position to spawn the video. Only if video is in use')
def main(expected_events, event_definition, max_window, cep_frequency, group_size, group_frequency,
         graph_x_size, interesting_objects, fps, precompile, text, graph, video, video_name, video_x_position,
         video_y_position):
    start_detecting(
        expected_events=expected_events,
        event_definition=event_definition,
        max_window=max_window,
        cep_frequency=cep_frequency,
        group_size=group_size,
        group_frequency=group_frequency,
        graph_x_size=graph_x_size,
        interesting_objects=interesting_objects,
        fps=fps,
        precompile=precompile,
        text=text,
        use_graph=graph,
        video=video,
        video_name=video_name,
        video_x_position=video_x_position,
        video_y_position=video_y_position
    )


if __name__ == '__main__':
    main()
