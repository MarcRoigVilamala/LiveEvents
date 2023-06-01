import itertools

from input.eventGeneration.fromFileEvents import FromFileEventGenerator
# If your event generation requires uncommon libraries, use local imports to avoid adding them to requirements


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


def create_file_3d_res_net_generator(conf, event_gen_conf):
    video_name = conf['input']['input_feed'].get('video_name')
    if conf['input'].get('video_name') is None:
        video_class = None
    else:
        video_class = video_name.split('_')[:-3]

    return FromFileEventGenerator('data/ProbLogEvents/{}/3DResNet/{}.pl'.format(video_class, video_name))


def create_file_at_least_generator(conf, event_gen_conf):
    video_name = conf['input']['input_feed'].get('video_name')
    if conf['input'].get('video_name') is None:
        video_class = None
    else:
        video_class = video_name.split('_')[:-3]

    return FromFileEventGenerator('data/ProbLogEvents/{}/AtLeast/{}.pl'.format(video_class, video_name))


def create_file_overlapping_generator(conf, event_gen_conf):
    video_name = conf['input']['input_feed'].get('video_name')
    if conf['input'].get('video_name') is None:
        video_class = None
    else:
        video_class = video_name.split('_')[:-3]

    return FromFileEventGenerator('data/ProbLogEvents/{}/Overlapping/{}.pl'.format(video_class, video_name))


def create_object_detector_generator(conf, event_gen_conf):
    import sys
    # TODO: Fix this
    print(
        'Using an Object Detector as an event generator may not work correctly at the moment (to be fixed)',
        file=sys.stderr
    )
    from input.eventGeneration.objectDetection.objectDetection import ObjectDetectorEventGenerator

    interesting_objects = event_gen_conf.get('interesting_objects')

    event_gen = ObjectDetectorEventGenerator(interesting_objects)
    return event_gen


def create_audio_generator(conf, event_gen_conf):
    import torch
    from input.eventGeneration.fromAudioNN import SoundVGGish, FromAudioNN

    classes = event_gen_conf.get(
        'classes',
        [
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
    )

    network = SoundVGGish(len(classes))
    network.load_state_dict(
        torch.load(
            event_gen_conf.get(
                'weights',
                'neuralNetworkWeights/neural_network_scenario100_2_1000_noise_0_00_epoch_0008.pt'
            )
        )
    )

    return FromAudioNN(
        classes=classes, network=network
    )


def create_silence_audio_generator(conf, event_gen_conf):
    import torch
    from input.eventGeneration.fromAudioNN import SoundVGGish, FromAudioNN

    classes = event_gen_conf.get(
        'classes',
        [
            'silence',
            'speech',
        ]
    )

    network = SoundVGGish(len(classes))
    network.load_state_dict(
        torch.load(
            event_gen_conf.get(
                'weights',
                'neuralNetworkWeights/neural_network_scenario303_5_noise_0_00_epoch_0004.pt'
            )
        )
    )

    return FromAudioNN(
        classes=classes, network=network
    )


def create_audio_neuroplytorch_generator(conf, event_gen_conf):
    from input.eventGeneration.Neuroplytorch.fromAudioNeuroplytorch import \
        generate_audio_neuroplytorch_event_gen

    return generate_audio_neuroplytorch_event_gen()


def create_nlp_generator(conf, event_gen_conf):
    from input.eventGeneration.fromNLP import FromNLP
    return FromNLP(
        model_name=event_gen_conf.get("model_name"),
        ignore=event_gen_conf.get("ignore", set())
    )


available_event_generators = {
    'File3DResNet': create_file_3d_res_net_generator,
    'FileAtLeast': create_file_at_least_generator,
    'FileOverlapping': create_file_overlapping_generator,
    # 'ObjectDetector': create_object_detector_generator,
    'FromAudioNN': create_audio_generator,
    'FromSilenceAudioNN': create_silence_audio_generator,
    'FromAudioNeuroplytorch': create_audio_neuroplytorch_generator,
    'FromNLP': create_nlp_generator,
}


def create_event_generator(conf):
    conf_event_generators = conf['input']['event_generators']

    if not conf_event_generators:
        raise ValueError("At least one type of Event Generator must be added using --add_event_generator")

    event_generation_list = []

    for event_gen_conf in conf_event_generators:
        event_gen_type = event_gen_conf['type']

        if event_gen_type in available_event_generators.keys():
            event_generation_list.append(
                available_event_generators[event_gen_type](conf, event_gen_conf)
            )
        else:
            raise ValueError("Unexpected value for event generator type: {}".format(event_gen_conf))

    return EventGenerator(event_generation_list)
