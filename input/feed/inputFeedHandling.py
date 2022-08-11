import sys


def create_input_feed(input_feed_type, audio_file, loop_at, video_class, video_name):
    if input_feed_type == 'VideoFeed':
        print(
            'Using a VideoFeed as an input may not work correctly at the moment (to be fixed)',
            file=sys.stderr
        )
        from input.feed.videoFeed import VideoFeed
        input_feed = VideoFeed(
            video_file='~/datasets/Video/UCF_CRIME/DemoVideos/{}/{}.mp4'.format(video_class, video_name),
            loop_at=loop_at
        )
    elif input_feed_type == 'AudioFeed':
        if audio_file is None:
            raise ValueError("--audio_file needs to be defined when using AudioFeed as the input_feed_type")
        from input.feed.audioFeed import AudioFeed
        input_feed = AudioFeed(audio_file)
    elif input_feed_type == 'LiveAudioFeed':
        from input.feed.liveAudioFeed import LiveAudioFeed
        if LiveAudioFeed is None:
            raise Exception("LiveAudioFeed cannot be used as it could not be imported. Make sure pyaudio is installed")
        input_feed = LiveAudioFeed()
    # elif input_feed_type == 'DemoAudioFeed':
    #     input_feed = DemoAudioFeed()
    else:
        raise ValueError("Unexpected value for input_feed_type: {}".format(input_feed_type))
    return input_feed
