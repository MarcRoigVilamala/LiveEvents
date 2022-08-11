import sys
import time
import click
import numpy as np

from confs.configuration import *
from input.eventGeneration.event import Event
from input.inputHandler import InputHandler
from output.outputHandler import OutputHandler
from ProbCEP.model import generate_model, update_evaluation, get_framework_files


def at_rate(iterable, rate):
    period = 1.0 / rate

    start = time.time()

    for i, v in enumerate(iterable):
        now = time.time()
        to_wait = period * i - (now - start)
        if to_wait > 0:
            time.sleep(to_wait)

        yield v


class LiveEvents(object):
    def __init__(self, conf):
        self.conf = conf

        # Get the required values from the configuration
        self.max_window = conf['logic']['max_window']
        self.cep_frequency = conf['logic']['cep_frequency']
        self.group_size = conf['logic']['group_size']
        self.group_frequency = conf['logic']['group_frequency']

        self.ce_threshold = conf['events']['ce_threshold']
        self.tracked_ce = conf['events']['tracked_ce']

        self.fps = conf['misc'].get('fps', 30.0)

        self.check_logic_parameters()

        # Generate handlers
        self.input_handler = InputHandler(self.conf)

        self.output_handler = OutputHandler(
            self.input_handler, conf['events']['tracked_ce'], conf
        )

        self.model = generate_model(
            [
                *conf['events']['event_definition'],
                *get_framework_files(conf['events'].get('use_framework', []))
            ],
            conf['logic'].get('precompile')
        )

        # Initialize values
        self.evaluation = {}

        self.complex_events = []

        self.window = []
        self.all_events = []  # All events will contain all the simple and complex events in the window

        self.last_complex_event = []
        self.current_complex_event = []

    def check_logic_parameters(self):
        if self.max_window < self.cep_frequency + self.group_frequency:
            print(
                'The window of events can not be smaller than the sum of the frequency of checking and grouping',
                file=sys.stderr
            )
            sys.exit(-1)

    @staticmethod
    def convert_for_event_generation(relevant_frames, diff):
        return [
            (i - diff, frame)
            for i, frame in relevant_frames
        ]

    @staticmethod
    def convert_after_event_generation(events, diff):
        return [
            Event(e.timestamp + diff, e.identifier, e.probability, e.event_type)
            for e in events
        ]

    @staticmethod
    def event_exists_in(event, event_list):
        for e in event_list:
            if e.timestamp == event.timestamp and e.identifier == event.identifier:
                return True

        return False

    def generate_simple_events(self, i, feed_i):
        # Every group_frequency, get the relevant events
        if not (i + 1) % self.group_frequency:
            # Check that we have enough frames for the group (preventing errors on first iterations)
            if len(self.window) >= self.group_size:
                relevant_frames = self.window[-self.group_size:]

                # Add the part to update the frame number for event generation
                relevant_frames = self.convert_for_event_generation(relevant_frames, i - feed_i)

                new_events = self.input_handler.event_generator.get_events(relevant_frames)

                # And add the part to convert back into events with the correct id
                new_events = self.convert_after_event_generation(new_events, i - feed_i)

                for e in new_events:
                    if not self.event_exists_in(e, self.all_events):
                        self.all_events.append(e)

    def generate_complex_events(self, i, output_update):
        new_evaluation = {}
        new_complex_events = []

        # Every cep_frequency frames, run the CEP part with the relevant events
        # The i - group_size >= -1 is for the first iteration, where we do not have all the relevant frames
        if not (i + 1) % self.cep_frequency and i - self.group_size >= -1:
            # print("Executing problog at {} for {} to {}".format(i, i - max_window + 1, i))

            # Remove the events that happened before the current window
            while self.all_events and self.all_events[0].timestamp < i - self.max_window:
                # While we have events and the first event is before the current window, remove the first event
                self.all_events = self.all_events[1:]

            new_evaluation = self.model.get_probabilities_precompile(
                existing_timestamps=np.arange(0, i + 1, self.group_frequency),
                query_timestamps=[i - self.group_size + 1],
                tracked_ce=self.tracked_ce,
                input_events=self.all_events
            )

            new_events = Event.from_evaluation(new_evaluation)
            self.all_events += new_events

            new_complex_events = [
                e
                for e in new_events
                if e.probability > self.ce_threshold
            ]

            self.update_current_complex_event(new_complex_events)

            output_update['new_evaluation'] = new_evaluation
            output_update['new_complex_events'] = new_complex_events
            output_update['last_complex_event'] = self.last_complex_event

        return new_evaluation, new_complex_events

    def update_current_complex_event(self, new_complex_events):
        if new_complex_events:
            self.current_complex_event += new_complex_events
        else:
            self.last_complex_event = self.current_complex_event
            self.current_complex_event = []

    def start_detecting(self):
        for i, (feed_i, frame) in at_rate(enumerate(self.input_handler.input_feed), self.fps):
            output_update = {
                'iteration': i,
                'feed_iteration': feed_i,
                'frame': frame  # Frame is the non-symbolic piece of information from the input stream
            }

            # Keep only the number of frames we need
            self.window.append((i, frame))
            self.window = self.window[-self.group_size:]

            self.generate_simple_events(i, feed_i)

            new_evaluation, new_complex_events = self.generate_complex_events(i, output_update)

            self.evaluation = update_evaluation(self.evaluation, new_evaluation)
            output_update['evaluation'] = self.evaluation
            self.complex_events += new_complex_events

            self.output_handler.update(output_update)

        self.output_handler.terminate_outputs(self.evaluation)

        return self.evaluation


@click.command()
@click.option(
    '--conf', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='Configuration file to use. Values from the file can be overwritten using other command line arguments.'
)
@click.option(
    '--tracked_ce', multiple=True, type=str,
    help='Name of the complex event that needs to be tracked. Use multiple times to track multiple complex events.'
)
@click.option(
    '--event_definition', '--add_to_model', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    multiple=True, help='File defining the rules for the complex events. Use multiple times for multiple files.'
)
@click.option(
    '--input_feed_type', type=click.Choice([
        'VideoFeed',
        'LiveAudioFeed',
        'AudioFeed',
        # 'DemoAudioFeed'
    ]),
    help='Should represent the type of input stream being used'
)
@click.option(
    '--use_framework', multiple=True,
    type=click.Choice(
        [
            'sequence',
            'eventCalculus'
        ]
    )
)
@click.option(
    '--add_event_generator', multiple=True,
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
    help='Audio file. Should be included if AudioFeed is selected as the input_feed_type'
)
@click.option(
    '-w', '--max_window', type=int,  # default=32,
    help='Maximum window size used in event definitions. '
         'At timestamp T, remove all simple events happening before T - max_window from the list.'
)
@click.option(
    '--cep_frequency', type=int,  # default=8,
    help='The logic inference is performed every cep_frequency iterations from the input feed. '
         'That is, every cep_frequency frames for video and every cep_frequency seconds for audio.'
)
@click.option(
    '-g', '--group_size', type=int,  # default=16,
    help='Number of iterations from the input feed considered to generate a complex event. '
         'Should be set to 16 frames for video and 1 second for audio for default configuration.'
)
@click.option(
    '-f', '--group_frequency', type=int,  # default=8,
    help='Frequency at which event generators are called, based on the number of iterations from the input feed. '
         'Usually, 8 frames for video (to have an overlapping of 8 frames) and 1 second for audio.'
)
@click.option(
    '--graph_x_size', type=int,
    help='Size of the x axis (time) for the graph. Only if graph is in use. If undefined, the system will attempt to '
         'use the appropriate size automatically'
)
@click.option(
    '-o', '--interesting_objects',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help='File defining the list of objects we care about from the object detector output'
)
@click.option(
    '--fps', type=float,
    help='Number of frames that are processed every second. Controls the speed at which the program processes the feed'
)
@click.option(
    '--precompile', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
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
    '--use_graph', '--graph', is_flag=True,
    help='If used, a live graph will be generated showing the values of the different complex events'
)
@click.option('--play_audio', '--audio', is_flag=True, help='If used, a live audio will be played')
@click.option('--play_video', '--video', is_flag=True, help='If used, a live video will be shown')
@click.option('--video_name', type=str, help='Name of the video for which we want to perform CEP')
@click.option('--video_x_position', type=int, help='X position to spawn the video. Only if video is in use')
@click.option('--video_y_position', type=int, help='Y position to spawn the video. Only if video is in use')
@click.option(
    '--loop_at', type=int, help='If used, the video will loop at the given number until a button is pressed'
)
@click.option('--button', is_flag=True, help='Use to create a button to stop the loop')
@click.option('--post_message', is_flag=True, help='Use to allow a HTTP POST message to stop the loop')
@click.option(
    '--zmq_address', type=str, help='Specify if you want to send messages through ZeroMQ'
)
@click.option(
    '-p', '--zmq_port', default=9999, type=int, help='Port to use for the ZeroMQ connection'
)
@click.option(
    '--ce_threshold', type=float, help='Threshold for above which probability we detect a complex event'
)
@click.option(
    '--video_scale', help='Scale of the video'
)
@click.option(
    '--mark_objects', is_flag=True, help='If used, objects will be marked in the video'
)
@click.option(
    '--save_graph_to', type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help='Save the generated graph to the given path. Requires .mp4 extension'
)
@click.option(
    '--sue_address', type=str, help='Specify if you want to send a message to SUE'
)
def main(conf, *args, **kwargs):
    if conf:
        conf = parse_configuration(conf_filename=conf)

        conf = update_configuration_values(
            conf, *args, **kwargs
        )
    else:
        conf = create_configuration(*args, **kwargs)

    assert check_conf_format(conf), "Incorrect configuration. Some required fields are likely missing (see above)"
    # save_configuration(remove_empty_values(conf), 'confs/worryingSirenDemo.json')

    live_events = LiveEvents(conf)

    live_events.start_detecting()


if __name__ == '__main__':
    main()
