import os
from itertools import cycle

import cv2


class VideoFeed(object):
    def __init__(self, video_file='/home/marc/Videos/UCF_CRIME/Crime/Abuse/Abuse001_x264.mp4'):
        self.frames = [
            cv2.imread('frames/Fighting006_x264/' + frame)
            for frame in sorted(os.listdir('frames/Fighting006_x264'))
        ]

        self.current_frame = -1

        self.loop = True

        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        # self.video = cv2.VideoCapture(0)
        # self.video = cv2.VideoCapture(video_file)

    # def __del__(self):
    #     self.video.release()

    def stop_loop(self):
        self.loop = False

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

        if self.current_frame == 32:
            if self.loop:
                self.current_frame = 0

        if self.current_frame >= len(self.frames):
            raise StopIteration()

        return self.current_frame, self.frames[self.current_frame]
