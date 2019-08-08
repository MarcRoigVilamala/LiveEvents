from itertools import cycle
from os import listdir

import cv2


class VideoFeed(object):
    def __init__(self, video_name='Fighting006'):
        self.frames = [
            cv2.imread('frames/{}/{}'.format(video_name, frame))
            for frame in sorted(listdir('frames/{}'.format(video_name)))
        ]

        self.current_frame = -1

        self.aux = 0

        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        # self.video = cv2.VideoCapture(0)
        # self.video = cv2.VideoCapture(video_file)

    # def __del__(self):
    #     self.video.release()

    def __iter__(self):
        return self
        # return cycle(self.frames)
        # return self.frames.__iter__()

        # self.current_frame += 1
        # self.current_frame %= len(self.frames)
        #
        # return self.frames[self.current_frame]

        # success, image = self.video.read()
        # while success:
        #     yield image
        #
        #     success, image = self.video.read()
        #
        # self.video.release()

    def __next__(self):
        self.current_frame += 1

        if self.aux < 10:
            if self.current_frame >= 16:
                self.aux += 1

            self.current_frame %= 16

        if len(self.frames) > self.current_frame:
            return self.current_frame, self.frames[self.current_frame]
        else:
            raise StopIteration()
