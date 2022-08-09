from output.liveEventsOutupt import LiveEventsOutput


class Text(LiveEventsOutput):
    def __init__(self):
        pass

    def finish_initialization(self):
        pass

    def update(self, output_update):
        if 'new_evaluation' in output_update:
            print(output_update['new_evaluation'])

    def terminate_output(self, evaluation, *args, **kwargs):
        print('################################################################################################')
        print(evaluation)
