import itertools

import torch

from input.eventGeneration.Neuroplytorch.fromAudioNeuroplytorch import generate_audio_neuroplytorch_event_gen
from input.eventGeneration.fromAudioNN import SoundVGGish, FromAudioNN
from input.eventGeneration.fromFileEvents import FromFileEventGenerator


class EventGenerator(object):
    def __init__(self, event_generators):
        self.event_generators = event_generators

    def get_events(self, enumerated_frames):
        return list(
            itertools.chain.from_iterable(
                [
                    event_gen.get_events(enumerated_frames)
                    for event_gen in self.event_generators
                ]
            )
        )


def create_event_generator(event_generator_types, interesting_objects, video_class, video_name):
    if not event_generator_types:
        raise ValueError("At least one type of Event Generator must be added using --add_event_generator")

    event_generation_list = []

    for event_gen_type in event_generator_types:
        if event_gen_type == 'File3DResNet':
            event_gen = FromFileEventGenerator('data/ProbLogEvents/{}/3DResNet/{}.pl'.format(video_class, video_name))
        elif event_gen_type == 'FileAtLeast':
            event_gen = FromFileEventGenerator('data/ProbLogEvents/{}/AtLeast/{}.pl'.format(video_class, video_name))
        elif event_gen_type == 'FileOverlapping':
            event_gen = FromFileEventGenerator('data/ProbLogEvents/{}/Overlapping/{}.pl'.format(video_class, video_name))
        # elif event_gen_type == 'ObjectDetector':
        #     # from eventGeneration.objectDetection.objectDetection import ObjectDetectorEventGenerator
        #     # from eventGeneration.hardCodedEvents import HardCodedObjectDetectorEventGenerator as ObjectDetectorEventGenerator
        #     # from eventGeneration.hardCodedEvents import HardCodedVideoEventGenerator as VideoEventGenerator
        #
        #     # Find which are the interesting objects
        #     if interesting_objects is None:
        #         interesting_objects_list = None
        #     else:
        #         with open(interesting_objects, 'r') as f:
        #             interesting_objects_list = [l.strip() for l in f]
        #
        #     event_gen = ObjectDetectorEventGenerator(interesting_objects_list)
        # elif event_gen_type == 'Video':
        #     event_gen = VideoEventGenerator()
        # elif event_gen_type == 'DemoFromAudioNN':
        #     event_gen = DemoFromAudioNN(
        #         [
        #             (i, '/home/marc/demos/AFM2020/VGGish/CutBang_edited_{}.pt'.format(i))
        #             for i in range(20)
        #         ]
        #     )
        elif event_gen_type == 'FromAudioNN':
            classes = [
                'airConditioner',
                'carHorn',
                'childrenPlaying',
                'dogBark',
                'drilling',
                'engineIdling',
                'gunShot',
                'jackhammer',
                'siren',
                'streetMusic'
            ]

            network = SoundVGGish(len(classes))
            network.load_state_dict(
                torch.load('neuralNetworkWeights/neural_network_scenario100_2_1000_noise_0_00_epoch_0008.pt')
            )

            event_gen = FromAudioNN(
                classes=classes, network=network
            )
        elif event_gen_type == 'FromLiveAudioNN':
            classes = [
                'silence',
                'speech',
            ]

            network = SoundVGGish(len(classes))
            network.load_state_dict(
                torch.load('neuralNetworkWeights/neural_network_scenario303_5_noise_0_00_epoch_0004.pt')
            )

            event_gen = FromAudioNN(
                classes=classes, network=network
            )
        elif 'FromAudioNeuroplytorch':
            if generate_audio_neuroplytorch_event_gen is None:
                raise Exception(
                    "FromAudioNeuroplytorch cannot be used due to ImportError. Ensure pytorch_lightning is installed"
                )
            event_gen = generate_audio_neuroplytorch_event_gen()
        else:
            raise ValueError("Unexpected value for add_event_generator: {}".format(event_gen_type))

        event_generation_list.append(event_gen)

    return EventGenerator(event_generation_list)
