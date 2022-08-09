from output.liveEventsOutupt import LiveEventsOutput


class CleanText(LiveEventsOutput):
    def __init__(self):
        pass

    def finish_initialization(self):
        pass

    def update(self, output_update):
        if 'new_complex_events' in output_update:
            print(
                "At timestamp {}: {}".format(
                    output_update['iteration'], ', '.join(
                        [e.to_nice_string() for e in output_update['new_complex_events']]
                    )
                )
            )

    def terminate_output(self, evaluation, *args, **kwargs):
        pass
