import sys

from input.feed.audioFeed import AudioFeed
from input.feed.liveAudioFeed import LiveAudioFeed
from input.feed.videoFeed import VideoFeed


def create_input_feed(input_feed_type, audio_file, loop_at, video_class, video_name):
    if input_feed_type == 'VideoFeed':
        print(
            'Using a VideoFeed as an input may not work correctly at the moment (to be fixed)',
            file=sys.stderr
        )
        input_feed = VideoFeed(
            video_file='~/datasets/Video/UCF_CRIME/DemoVideos/{}/{}.mp4'.format(video_class, video_name),
            loop_at=loop_at
        )
    elif input_feed_type == 'AudioFeed':
        if audio_file is None:
            raise ValueError("--audio_file needs to be defined when using AudioFeed as the INPUT_FEED_TYPE")
        input_feed = AudioFeed(audio_file)
    elif input_feed_type == 'LiveAudioFeed':
        if LiveAudioFeed is None:
            raise Exception("LiveAudioFeed cannot be used as it could not be imported. Make sure pyaudio is installed")
        input_feed = LiveAudioFeed()
    # elif input_feed_type == 'DemoAudioFeed':
    #     input_feed = DemoAudioFeed()
    else:
        raise ValueError("Unexpected value for INPUT_FEED_TYPE: {}".format(input_feed_type))
    return input_feed
