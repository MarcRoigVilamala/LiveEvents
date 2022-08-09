import sys
import time
import click
import numpy as np

from input.endLoop.endLoop import create_end_loop_triggers
from input.feed.inputFeedHandling import create_input_feed
from input.eventGeneration.event import Event
from input.eventGeneration.eventGeneration import create_event_generator
from output.outputHandler import OutputHandler
from ProbCEP.model import generate_model, update_evaluation


def at_rate(iterable, rate):
    period = 1.0 / rate

    start = time.time()

    for i, v in enumerate(iterable):
        now = time.time()
        to_wait = period * i - (now - start)
        if to_wait > 0:
            time.sleep(to_wait)

        yield v


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


def event_exists_in(event, event_list):
    for e in event_list:
        if e.timestamp == event.timestamp and e.identifier == event.identifier:
            return True

    return False


def start_detecting(input_feed, event_generator, expected_events, event_definition, add_to_model, max_window, cep_frequency,
                    group_size, group_frequency, graph_x_size, fps, precompile, text, clean_text, timings, use_graph, play_audio, audio_file,
                    play_video, video_name, video_x_position, video_y_position, loop_at, button, post_message, address,
                    port, ce_threshold, video_scale, mark_objects, save_graph_to, sue_address):
    if max_window < cep_frequency + group_frequency:
        print(
            'The window of events can not be smaller than the sum of the frequency of checking and grouping',
            file=sys.stderr
        )
        sys.exit(-1)

    with open(expected_events) as f:
        expected_events_list = [l.strip() for l in f]

    output_handler = OutputHandler(
        input_feed, event_generator, expected_events_list, event_definition, add_to_model, max_window, cep_frequency,
        group_size, group_frequency, graph_x_size, fps, precompile, text, clean_text, timings, use_graph, play_audio,
        audio_file, play_video, video_name, video_x_position, video_y_position, loop_at, button, post_message, address,
        port, ce_threshold, video_scale, mark_objects, save_graph_to, sue_address
    )

    window = []
    all_events = []  # All events will contain all the simple and complex events in the window

    model = generate_model(
        [event_definition, *add_to_model],
        precompile
    )

    evaluation = {}
    complex_events = []

    last_complex_event = []
    current_complex_event = []

    create_end_loop_triggers(input_feed, loop_at, button, post_message)

    for i, (feed_i, frame) in at_rate(enumerate(input_feed), fps):
        output_update = {
            'iteration': i,
            'feed_iteration': feed_i,
            'frame': frame  # Frame is the non-symbolic piece of information from the input stream
        }

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
                relevant_frames = convert_for_event_generation(relevant_frames, i - feed_i)

                new_events = event_generator.get_events(relevant_frames)

                # And add the part to convert back into events with the correct id
                new_events = convert_after_event_generation(new_events, i - feed_i)

                for e in new_events:
                    if not event_exists_in(e, all_events):
                        all_events.append(e)

        # Every cep_frequency frames, run the CEP part with the relevant events
        # The i - group_size >= -1 is for the first iteration, where we do not have all the relevant frames
        if not (i + 1) % cep_frequency and i - group_size >= -1:
            # print("Executing problog at {} for {} to {}".format(i, i - max_window + 1, i))

            # Remove the events that happened before the current window
            while all_events and all_events[0].timestamp < i - max_window:
                # While we have events and the first event is before the current window, remove the first event
                all_events = all_events[1:]

            new_evaluation = model.get_probabilities_precompile(
                existing_timestamps=np.arange(0, i + 1, group_frequency),
                query_timestamps=[i - group_size + 1],
                expected_events=expected_events_list,
                input_events=all_events
            )
            output_update['new_evaluation'] = new_evaluation

            new_events = Event.from_evaluation(new_evaluation)

            all_events += new_events

            evaluation = update_evaluation(evaluation, new_evaluation)
            output_update['evaluation'] = evaluation

            new_complex_events = [
                e
                for e in new_events
                if e.probability > ce_threshold
            ]
            output_update['new_complex_events'] = new_complex_events

            if new_complex_events:
                current_complex_event += new_complex_events
            else:
                last_complex_event = current_complex_event
                current_complex_event = []
            output_update['last_complex_event'] = last_complex_event

            complex_events += new_complex_events

        output_handler.update(output_update)

    output_handler.terminate_outputs(evaluation)


@click.command()
@click.argument('expected_events', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument('event_definition', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument(
    'input_feed_type', type=click.Choice([
        'VideoFeed',
        'LiveAudioFeed',
        'AudioFeed',
        # 'DemoAudioFeed'
    ]),
    # input_feed_type should represent the type of input stream being used
)
@click.option(
    '--add_to_model', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), multiple=True,
    help='Further ProbLog files to be added to the model generation'
)
@click.option(
    '--add_event_generator', multiple=True, required=True,
    type=click.Choice(
        [
            'File3DResNet',
            'FileAtLeast',
            'FileOverlapping',
            'ObjectDetector',
            'Video',
            'FromAudioNN',
            'FromLiveAudioNN',
            'FromAudioNeuroplytorch',
            # 'DemoFromAudioNN'
        ]
    ),
    help='Event generators process the input feed each iteration and extract the events from it'
)
@click.option(
    '--audio_file', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='Audio file. Should be included if AudioFeed is selected as the INPUT_FEED_TYPE'
)
@click.option(
    '-w', '--max_window', default=32,
    help='Maximum window size used in event definitions. '
         'At timestamp T, remove all simple events happening before T - max_window from the list.'
)
@click.option(
    '--cep_frequency', default=8,
    help='The logic inference is performed every cep_frequency iterations from the input feed. '
         'That is, every cep_frequency frames for video and every cep_frequency seconds for audio.'
)
@click.option(
    '-g', '--group_size', default=16,
    help='Number of iterations from the input feed considered to generate a complex event. '
         'Should be set to 16 frames for video and 1 second for audio for default configuration.'
)
@click.option(
    '-f', '--group_frequency', default=8,
    help='Frequency at which event generators are called, based on the number of iterations from the input feed. '
         'Usually, 8 frames for video (to have an overlapping of 8 frames) and 1 second for audio.'
)
@click.option(
    '--graph_x_size', default=None, type=int,
    help='Size of the x axis (time) for the graph. Only if graph is in use. If undefined, the system will attempt to '
         'use the appropriate size automatically'
)
@click.option(
    '-o', '--interesting_objects', default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='File defining the list of objects we care about from the object detector output'
)
@click.option(
    '--fps', default=30.0,
    help='Number of frames that are processed every second. Controls the speed at which the program processes the feed'
)
@click.option(
    '--precompile', default=None, type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='JSON file defining the inputs and outputs for which we can use precompilation'
)
@click.option(
    '--text', is_flag=True, help='If used, a live text will be printed with the values of the different complex events'
)
@click.option(
    '--clean_text', is_flag=True,
    help='If used, a clean live text will be printed with the values of the different complex events. '
         'This will only include complex events with a confidence above the threshold'
)
@click.option(
    '--timings', is_flag=True, help='If used, the system will output messages indicating the time performance'
)
@click.option(
    '--graph', is_flag=True,
    help='If used, a live graph will be generated showing the values of the different complex events'
)
@click.option('--audio', is_flag=True, help='If used, a live audio will be played')
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
    '--ce_threshold', default=0.5, help='Threshold for above which probability we detect a complex event'
)
@click.option(
    '--video_scale', default=1.0, help='Scale of the video'
)
@click.option(
    '--mark_objects', is_flag=True, help='If used, objects will be marked in the video'
)
@click.option(
    '--save_graph_to', type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help='Save the generated graph to the given path. Requires .mp4 extension'
)
@click.option(
    '--sue_address', default=None, type=str, help='Specify if you want to send a message to SUE'
)
def main(expected_events, event_definition, input_feed_type, add_to_model, add_event_generator, audio_file, max_window,
         cep_frequency, group_size, group_frequency, graph_x_size, interesting_objects, fps, precompile, text,
         clean_text, timings, graph, audio, video, video_name, video_x_position, video_y_position, loop_at, button,
         post_message, address, port, ce_threshold, video_scale, mark_objects, save_graph_to, sue_address):
    if video_name is None:
        video_class = None
    else:
        video_class = video_name[:-8]

    event_generator = create_event_generator(add_event_generator, interesting_objects, video_class, video_name)

    input_feed = create_input_feed(input_feed_type, audio_file, loop_at, video_class, video_name)

    start_detecting(
        input_feed=input_feed,
        event_generator=event_generator,
        expected_events=expected_events,
        event_definition=event_definition,
        add_to_model=add_to_model,
        max_window=max_window,
        cep_frequency=cep_frequency,
        group_size=group_size,
        group_frequency=group_frequency,
        graph_x_size=graph_x_size,
        fps=fps,
        precompile=precompile,
        text=text,
        clean_text=clean_text,
        timings=timings,
        use_graph=graph,
        play_audio=audio,
        audio_file=audio_file,
        play_video=video,
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
        mark_objects=mark_objects,
        save_graph_to=save_graph_to,
        sue_address=sue_address
    )


if __name__ == '__main__':
    main()
