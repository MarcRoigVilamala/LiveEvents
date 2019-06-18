from eventGeneration.event import Event
from eventGeneration.objectDetection.objectDetection import get_obj_det_events


def get_events(enumerated_frames, interesting_objects):
    return get_obj_det_events(enumerated_frames, interesting_objects) + get_video_events(enumerated_frames)


def get_video_events(enumerated_frames):
    return []
