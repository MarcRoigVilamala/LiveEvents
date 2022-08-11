from input.endLoop.endLoop import create_end_loop_triggers
from input.feed.inputFeedHandling import create_input_feed
from input.eventGeneration.eventGeneration import create_event_generator


class InputHandler(object):
    def __init__(self, conf):
        if conf['input'].get('video_name') is None:
            video_class = None
        else:
            video_class = conf['input']['video_name'][:-8]

        self.input_feed = create_input_feed(
            conf['input']['input_feed_type'],
            conf['input'].get('audio_file'),
            conf['input'].get('loop_at'),
            video_class,
            conf['input'].get('video_name')
        )

        self.event_generator = create_event_generator(
            conf['input']['add_event_generator'],
            conf['input'].get('interesting_objects'),
            video_class,
            conf['input'].get('video_name')
        )

        self._handle_other_inputs(conf)  # This should handle any input data that is not the input feeds directly

    def _handle_other_inputs(self, conf):
        if conf['input'].get('loop_at'):
            create_end_loop_triggers(
                self.input_feed,
                conf['input'].get('button'),
                conf['input'].get('post_message')
            )
