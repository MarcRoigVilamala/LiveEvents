import sys


def create_video_feed(conf, input_feed_conf):
    print(
        'Using a VideoFeed as an input may not work correctly at the moment (to be fixed)',
        file=sys.stderr
    )
    from input.feed.videoFeed import VideoFeed

    loop_at = conf['input'].get('loop_at')
    video_name = input_feed_conf.get('video_name')
    if video_name is None:
        raise ValueError('--video_name needs to be defined when using VideoFeed as the input feed')

    video_class = video_name.split('_')[:-3]

    return VideoFeed(
        video_file='~/datasets/Video/UCF_CRIME/DemoVideos/{}/{}.mp4'.format(video_class, video_name),
        loop_at=loop_at
    )


def create_audio_feed(conf, input_feed_conf):
    from input.feed.audioFeed import AudioFeed

    audio_file = input_feed_conf.get('audio_file')
    if audio_file is None:
        raise ValueError("--audio_file needs to be defined when using AudioFeed as the input feed")

    return AudioFeed(audio_file)


def create_live_audio_feed(conf, input_feed_conf):
    from input.feed.liveAudioFeed import LiveAudioFeed
    if LiveAudioFeed is None:
        raise Exception("LiveAudioFeed cannot be used as it could not be imported. Make sure pyaudio is installed")
    return LiveAudioFeed()


def create_from_json_reddit_feed(conf, input_feed_conf):
    from input.feed.fromJsonRedditFeed import FromJsonRedditFeed
    return FromJsonRedditFeed(from_file=input_feed_conf['from_file'])


def create_from_post_reddit_feed(conf, input_feed_conf):
    from input.feed.fromPostRedditFeed import FromPostRedditFeed
    return FromPostRedditFeed(
        from_post=input_feed_conf['from_post'],
        replace_more_limit=input_feed_conf.get('replace_more_limit', 0),
        praw_name=input_feed_conf.get('praw_name', 'LiveEvents'),
        max_comments=input_feed_conf.get('max_comments', None)
    )


def create_from_pickle_reddit_feed(conf, input_feed_conf):
    from input.feed.fromPickleRedditFeed import FromPickleRedditFeed
    return FromPickleRedditFeed(
        from_pickle=input_feed_conf['from_pickle'],
        max_comments=input_feed_conf.get('max_comments', None)
    )


def create_demo_audio_feed(conf, input_feed_conf):
    from input.feed.demoAudioFeed import DemoAudioFeed
    return DemoAudioFeed()


input_feeds = {
    'VideoFeed': create_video_feed,
    'AudioFeed': create_audio_feed,
    'LiveAudioFeed': create_live_audio_feed,
    'FromJsonRedditFeed': create_from_json_reddit_feed,
    'FromPostRedditFeed': create_from_post_reddit_feed,
    'FromPickleRedditFeed': create_from_pickle_reddit_feed,
    # 'DemoAudioFeed': create_demo_audio_feed,
}


def create_input_feed(conf):
    input_feed_conf = conf['input']['input_feed']

    input_feed_type = input_feed_conf['type']

    if input_feed_type in input_feeds:
        return input_feeds[input_feed_type](conf, input_feed_conf)
    else:
        raise ValueError("Unexpected value for input_feed_type: {}".format(input_feed_type))
