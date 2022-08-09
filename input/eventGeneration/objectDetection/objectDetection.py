import pandas as pd

from input.eventGeneration.event import Event
from input.eventGeneration.objectDetection.pytorch_objectdetect.PyTorch_Object_Detection import detect_image, parse_results
from input.translations.objects2average import count_beta as average_count_beta


class ObjectDetectorEventGenerator(object):
    COLUMNS = ['time', 'class', 'score', 'x1', 'y1', 'x2', 'y2']

    def __init__(self, interesting_objects=None):
        self.interesting_objects = interesting_objects

        self.objects = pd.DataFrame([], columns=self.COLUMNS)

        self.last_frame_detected = -1

    @staticmethod
    def object_detection(enumerated_frames):
        res = {}

        for i, frame in enumerated_frames:
            detection = detect_image(frame)

            res[i] = parse_results(detection, frame)

        return res

    def objects_to_pandas(self, objects):
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
                if not self.interesting_objects or obj['class'] in self.interesting_objects
            ]

        pd_objects = pd.DataFrame(data, columns=self.COLUMNS)

        return pd_objects

    @staticmethod
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

    def get_objects(self, enumerated_frames):
        new_objects = self.object_detection(enumerated_frames)

        return self.objects_to_pandas(new_objects)

    def get_events(self, enumerated_frames):
        timestamp = enumerated_frames[0][0]
        n_frames = len(enumerated_frames)

        # We can forget about the frames from before the first timestamp, since we will not need them anymore
        self.objects = self.objects[self.objects['time'] >= timestamp]

        # We may have already performed the object detection on some of the frames, so we filter those out
        frames_to_detect = filter(
            lambda x: x[0] > self.last_frame_detected,
            enumerated_frames
        )

        self.objects = self.objects.append(
            self.get_objects(frames_to_detect),
            ignore_index=True
        )

        # Update the last frame where we have preformed object detection
        self.last_frame_detected = enumerated_frames[-1][0]

        return self.get_average_events(self.objects, timestamp, n_frames)
