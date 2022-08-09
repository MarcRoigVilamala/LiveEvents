import cv2
import pandas as pd

from output.liveEventsOutupt import LiveEventsOutput

VIDEO_WINDOW_NAME = 'CCTV Feed'

# TODO: Fix video case. May not work correctly at the moment
class Video(LiveEventsOutput):
    def __init__(self, x, y, video_scale, video_name, mark_objects):
        self.video_scale = video_scale

        if mark_objects:
            self.objects_detected = get_pre_detected_objects(video_name)
        else:
            self.objects_detected = None

        cv2.namedWindow(VIDEO_WINDOW_NAME)
        cv2.moveWindow(VIDEO_WINDOW_NAME, x, y)

    def finish_initialization(self):
        pass

    def update(self, output_update):
        if 'frame' in output_update:
            if self.objects_detected is not None:
                showing_frame = add_objects_to_frame(
                    output_update['frame'], self.objects_detected, output_update['feed_i']
                )
            else:
                showing_frame = output_update['frame']

            update_video(showing_frame, scale=self.video_scale)

    def terminate_output(self, *args, **kwargs):
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass


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


def get_pre_detected_objects(video_name):
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

    return objects_detected
