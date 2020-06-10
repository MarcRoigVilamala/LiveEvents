import json
import sys
import threading
import time

import cv2
import click
import numpy as np

from PyProbEC.model import Model
from connection import Connection
from myHttpReceiver import create_http_reciever
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

import tkinter as tk
import pandas as pd

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


def generate_model(event_definition, precompile, semiring=None):
    if precompile:
        with open(precompile, 'r') as f:
            json_precompile = json.load(f)

        precomp_args = PreCompilationArguments(
            input_clauses=[Event(**e) for e in json_precompile['input_clauses']],
            queries=[EventQuery(**q) for q in json_precompile['queries']]
        )

        return Model([event_definition], precomp_args, semiring)
    else:
        return Model([event_definition], semiring=semiring)


def initialize_video(x, y):
    cv2.namedWindow(VIDEO_WINDOW_NAME)
    cv2.moveWindow(VIDEO_WINDOW_NAME, x, y)


def update_video(frame, scale=None):
    if scale is not None:
        width = int(frame.shape[1] * scale)
        height = int(frame.shape[0] * scale)
        dim = (width, height)

        resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    else:
        resized = frame

    cv2.imshow(VIDEO_WINDOW_NAME, resized)
    cv2.waitKey(1)


def convert_for_event_generation(relevant_frames, diff):
    return [
        (i - diff, frame)
        for i, frame in relevant_frames
    ]


def convert_after_event_generation(events, diff):
    return [
        Event(e.timestamp + diff, e.identifier, e.probability, e.event_type)
        for e in events
    ]


def create_loop_button(video_input):
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()

    def com():
        video_input.stop_loop()
        # root.destroy()

    button = tk.Button(
        frame,
        text="Start Event",
        command=com
    )
    button.pack(side=tk.LEFT)

    root.mainloop()


def add_objects_to_frame(frame, objects_detected, video_i):
    for i, obj in objects_detected[objects_detected['time'] == video_i].iterrows():
        # Should be this but labels on the csv are wrong
        cv2.rectangle(frame, (obj['x1'], obj['y1']), (obj['x2'], obj['y2']), (255, 0, 0), 2)
        # cv2.rectangle(frame, (obj['x1'], obj['x2']), (obj['y1'], obj['y2']), (0, 0, 255), 2)

        cv2.putText(
            frame,
            obj['class'],
            (obj['x1'], obj['y1']),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            1
        )

    return frame


def start_detecting(expected_events, event_definition, max_window, cep_frequency, group_size, group_frequency,
                    graph_x_size, interesting_objects, fps, precompile, text, use_graph, video, video_name,
                    video_x_position, video_y_position, loop_at, button, post_message, address, port, ce_threshold,
                    video_scale, object_mark, save_graph_to):
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
    if use_graph or save_graph_to:
        graph = Graph(graph_x_size, expected_events_list, ce_threshold, save_graph_to)
    else:
        graph = None

    if video:
        initialize_video(video_x_position, video_y_position)

    video_class = video_name[:-8]

    video_input = VideoFeed(
        video_file='/home/marc/Videos/UCF_CRIME/Crime/{}/{}.mp4'.format(video_class, video_name),
        loop_at=loop_at
    )

    event_generator = EventGenerator(
        [
            # ObjectDetectorEventGenerator(interesting_objects_list),
            # VideoEventGenerator()
            FromFileEventGenerator('ProbLogEvents/{}/3DResNet/{}.pl'.format(video_class, video_name)),
            FromFileEventGenerator('ProbLogEvents/{}/AtLeast/{}.pl'.format(video_class, video_name)),
            FromFileEventGenerator('ProbLogEvents/{}/Overlapping/{}.pl'.format(video_class, video_name))
        ]
    )

    if object_mark:
        objects_detected = pd.read_csv(
            'ObjectDetection/{}.csv'.format(video_name),
            delimiter=','
        )

        pad_x = 104.0
        pad_y = 0.0
        unpad_h = 416.0
        unpad_w = 312.0
        img_shape = (320, 240)

        print(objects_detected)
        objects_detected['box_h'] = ((objects_detected['y2'] - objects_detected['y1']) / unpad_h) * img_shape[0]
        objects_detected['box_w'] = ((objects_detected['x2'] - objects_detected['x1']) / unpad_w) * img_shape[1]
        objects_detected['y1'] = objects_detected['y1'].apply(lambda y1: ((y1 - pad_y // 2) / unpad_h) * img_shape[0])
        objects_detected['x1'] = objects_detected['x1'].apply(lambda x1: ((x1 - pad_x // 2) / unpad_w) * img_shape[1])
        objects_detected['x2'] = objects_detected['x1'] + objects_detected['box_w']
        objects_detected['y2'] = objects_detected['y1'] + objects_detected['box_h']

        for col in ['x1', 'x2', 'y1', 'y2']:
            objects_detected[col] = objects_detected[col].apply(int)
        print(objects_detected)
    else:
        objects_detected = None

    window = []
    events = []

    model = generate_model(event_definition, precompile)

    if address:
        connection = Connection(address, port)
    else:
        connection = None

    evaluation = {}
    complex_events = []

    last_complex_event = []
    current_complex_event = []

    if loop_at:
        if button:
            thread1 = threading.Thread(target=create_loop_button, args=(video_input, ))
            thread1.start()

        if post_message:
            thread2 = threading.Thread(target=create_http_reciever, args=(video_input,))
            thread2.start()

    for i, (video_i, frame) in at_rate(enumerate(video_input), fps):
        # if i > 8008:
        #     break
        if video:
            if objects_detected is not None:
                showing_frame = add_objects_to_frame(frame, objects_detected, video_i)
            else:
                showing_frame = frame

            update_video(showing_frame, scale=video_scale)

        # Keep only the number of frames we need
        window.append((i, frame))
        window = window[-group_size:]

        # Every group_frequency, get the relevant events
        if not (i + 1) % group_frequency:
            # print("Generating events at {} for {} to {}".format(i, i - group_size + 1, i))

            # Check that we have enough frames for the group (preventing errors on first iterations)
            if len(window) >= group_size:
                relevant_frames = window[-group_size:]

                # Add the part to update the frame number for event generation
                relevant_frames = convert_for_event_generation(relevant_frames, i - video_i)

                new_events = event_generator.get_events(relevant_frames)

                # And add the part to convert back into events with the correct id
                new_events = convert_after_event_generation(new_events, i - video_i)

                events += new_events

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

            new_events = Event.from_evaluation(new_evaluation)

            events += new_events

            evaluation = update_evaluation(evaluation, new_evaluation)

            new_complex_events = [
                e
                for e in new_events
                if e.probability > ce_threshold
            ]

            if new_complex_events:
                current_complex_event += new_complex_events
            else:
                last_complex_event = current_complex_event
                current_complex_event = []

            complex_events += new_complex_events

            if text:
                print(new_evaluation)

            if connection:
                if not new_complex_events and last_complex_event:
                    max_prob = max(
                        [
                            ce.probability
                            for ce in last_complex_event
                            if ce.identifier.split(' = ')[0] == 'videoAndObjDet'
                        ]
                    )

                    the_complex_event = [
                        ce
                        for ce in last_complex_event
                        if ce.identifier.split(' = ')[0] == 'videoAndObjDet' and ce.probability == max_prob
                    ][0]

                    connection.send(
                        [the_complex_event]
                    )

                    # connection.send(
                    #     [
                    #         ce
                    #         for ce in new_complex_events
                    #         if ce.identifier.split(' = ')[0] == 'videoAndObjDet' and ce.probability == max_prob
                    #     ]
                    # )

            if graph:
                graph.update(evaluation)

    print('################################################################################################')
    print(evaluation)

    if use_graph:
        input('Press enter to finish')

    if graph:
        graph.close()

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
@click.option(
    '--loop_at', default=None, type=int,
    help='If used, the video will loop at the given number until a button is pressed'
)
@click.option('--button', is_flag=True, help='Use to create a button to stop the loop')
@click.option('--post_message', is_flag=True, help='Use to allow a HTTP POST message to stop the loop')
@click.option(
    '--address', default=None, type=str, help='Specify if you want to send messages through ZeroMQ'
)
@click.option(
    '-p', '--port', default=9999, help='Port to use for the ZeroMQ connection'
)
@click.option(
    '--ce_threshold', default=0.01, help='Threshold for above which probability we detect a complex event'
)
@click.option(
    '--video_scale', default=1.0, help='Scale of the video'
)
@click.option(
    '--object_mark', is_flag=True, help='If used, objects will be marked in the video'
)
@click.option(
    '--save_graph_to', type=click.Path(file_okay=True, dir_okay=False, writable=True)
)
def main(expected_events, event_definition, max_window, cep_frequency, group_size, group_frequency,
         graph_x_size, interesting_objects, fps, precompile, text, graph, video, video_name, video_x_position,
         video_y_position, loop_at, button, post_message, address, port, ce_threshold, video_scale, object_mark,
         save_graph_to):
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
        video_y_position=video_y_position,
        loop_at=loop_at,
        button=button,
        post_message=post_message,
        address=address,
        port=port,
        ce_threshold=ce_threshold,
        video_scale=video_scale,
        object_mark=object_mark,
        save_graph_to=save_graph_to
    )


if __name__ == '__main__':
    main()
