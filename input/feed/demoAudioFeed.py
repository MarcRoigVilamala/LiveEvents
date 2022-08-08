class DemoAudioFeed(object):
    def __init__(self):
        pass

    def __iter__(self):
        for i in range(20):
            yield i, i
