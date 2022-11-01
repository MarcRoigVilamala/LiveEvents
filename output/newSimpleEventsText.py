from output.liveEventsOutupt import LiveEventsOutput


class NewSimpleEventsText(LiveEventsOutput):
    def __init__(self):
        pass

    def finish_initialization(self):
        pass

    def update(self, output_update):
        if 'new_simple_events' in output_update:
            print(output_update['new_simple_events'])

    def terminate_output(self, evaluation, *args, **kwargs):
        pass
