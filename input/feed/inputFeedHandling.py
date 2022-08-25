import sys


def create_video_feed(conf):
    print(
        'Using a VideoFeed as an input may not work correctly at the moment (to be fixed)',
        file=sys.stderr
    )
    from input.feed.videoFeed import VideoFeed

    loop_at = conf['input'].get('loop_at')
    video_name = conf['input'].get('video_name')
    if conf['input'].get('video_name') is None:
        video_class = None
    else:
        video_class = video_name

    return VideoFeed(
        video_file='~/datasets/Video/UCF_CRIME/DemoVideos/{}/{}.mp4'.format(video_class, video_name),
        loop_at=loop_at
    )


def create_audio_feed(conf):
    from input.feed.audioFeed import AudioFeed

    audio_file = conf['input'].get('audio_file')
    if audio_file is None:
        raise ValueError("--audio_file needs to be defined when using AudioFeed as the input_feed_type")

    return AudioFeed(audio_file)


def create_live_audio_feed(conf):
    from input.feed.liveAudioFeed import LiveAudioFeed
    if LiveAudioFeed is None:
        raise Exception("LiveAudioFeed cannot be used as it could not be imported. Make sure pyaudio is installed")
    return LiveAudioFeed()


def create_demo_audio_feed(conf):
    from input.feed.demoAudioFeed import DemoAudioFeed
    return DemoAudioFeed()


input_feeds = {
    'VideoFeed': create_video_feed,
    'AudioFeed': create_audio_feed,
    'LiveAudioFeed': create_live_audio_feed,
    # 'DemoAudioFeed': create_demo_audio_feed,
}


def create_input_feed(conf):
    input_feed_type = conf['input']['input_feed_type']

    if input_feed_type in input_feeds:
        return input_feeds[input_feed_type](conf)
    else:
        raise ValueError("Unexpected value for input_feed_type: {}".format(input_feed_type))
