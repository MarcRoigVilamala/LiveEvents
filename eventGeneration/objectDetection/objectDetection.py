import pandas as pd

from eventGeneration.event import Event
from eventGeneration.objectDetection.pytorch_objectdetect.PyTorch_Object_Detection import detect_image, parse_results
from eventGeneration.translations.objects2average import count_beta as average_count_beta


def object_detection(enumerated_frames):
    res = {}

    for i, frame in enumerated_frames:
        detection = detect_image(frame)

        res[i] = parse_results(detection)

    return res


def objects_to_pandas(objects, interesting_objects):
    data = []

    for timestamp, frame_objects in objects.items():
        data += [
            [
                timestamp,
                obj['class'],
                obj['score'],
                obj['bounding_box']['x1'],
                obj['bounding_box']['y1'],
                obj['bounding_box']['x2'],
                obj['bounding_box']['y2']
            ] for obj in frame_objects
            if not interesting_objects or obj['class'] in interesting_objects
        ]

    pd_objects = pd.DataFrame(data, columns=['time', 'class', 'score', 'x1', 'y1', 'x2', 'y2'])

    return pd_objects


def get_average_events(objects, timestamp, n_frames):
    average = average_count_beta(objects, timestamp, n_frames)

    return [
        Event(
            timestamp=timestamp,
            event='atLeast({}, {})'.format(occurences, class_name),
            probability=prob
        )
        for class_name, class_averages in average.items()
        for occurences, prob in class_averages.items()
    ]


def get_obj_det_events(enumerated_frames, interesting_objects):
    timestamp = enumerated_frames[0][0]
    n_frames = len(enumerated_frames)

    events = []

    objects = object_detection(enumerated_frames)

    pd_objects = objects_to_pandas(objects, interesting_objects)

    events += get_average_events(pd_objects, timestamp, n_frames)

    return events
