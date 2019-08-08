from itertools import cycle

import cv2


class VideoFeed(object):
    def __init__(self, video_file='/home/marc/Videos/UCF_CRIME/Crime/Abuse/Abuse001_x264.mp4'):
        # self.frames = [
        #     open('frames/frame0.jpg'.format(frame), 'rb').read()
        #     for frame in range(100)
        # ]

        # self.current_frame = -1

        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        # self.video = cv2.VideoCapture(0)
        self.video = cv2.VideoCapture(video_file)

    def __del__(self):
        self.video.release()

    def __iter__(self):
        # return cycle(self.frames)
        # return self.frames.__iter__()

        # self.current_frame += 1
        # self.current_frame %= len(self.frames)
        #
        # return self.frames[self.current_frame]

        success, image = self.video.read()
        while success:
            yield image

            success, image = self.video.read()

        self.video.release()
