from input.endLoop.endLoop import create_end_loop_triggers
from input.feed.inputFeedHandling import create_input_feed
from input.eventGeneration.eventGeneration import create_event_generator


class InputHandler(object):
    def __init__(self, conf):
        self.input_feed = create_input_feed(conf)

        self.event_generator = create_event_generator(conf)

        # Finally handle any input data that is not the input feeds or event generators directly
        self._handle_other_inputs(conf)

    def _handle_other_inputs(self, conf):
        if conf['input'].get('loop_at'):
            create_end_loop_triggers(
                self.input_feed,
                conf['input'].get('button'),
                conf['input'].get('post_message')
            )
