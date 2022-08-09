import pickle

import zmq
from output.connection_output.syncClock import now
from output.liveEventsOutupt import LiveEventsOutput


class ZMQConnection(LiveEventsOutput):
    def __init__(self, address, port):
        context = zmq.Context.instance()

        self.socket = context.socket(zmq.PUB)
        self.socket.connect("tcp://{}:{}".format(address, port))
        # self.socket.bind("tcp://*:{}".format(port))

        # Initialize the connection for the timestamp
        now()

    def send(self, complex_events):
        for ce in complex_events:
            print('Sending a fight event with probability {}'.format(ce.probability))

            message = pickle.dumps(['fight', 'VIOLENCE', now(), ce.probability])

            self.socket.send_multipart(
                [
                    "{topic}".format(topic='VIOLENCE').encode(),
                    message
                ]
            )

    def finish_initialization(self):
        pass

    def update(self, output_update):
        if 'new_complex_events' in output_update:
            new_complex_events = output_update['new_complex_events']
            last_complex_event = output_update['last_complex_event']

            if not new_complex_events and last_complex_event:
                max_prob = max(
                    [
                        ce.probability
                        for ce in last_complex_event
                        if ce.identifier.split(' = ')[0] == 'videoAndObjDet'
                    ]
                )

                the_complex_event = [
                    ce
                    for ce in last_complex_event
                    if ce.identifier.split(' = ')[0] == 'videoAndObjDet' and ce.probability == max_prob
                ][0]

                self.send([the_complex_event])

                # connection.send(
                #     [
                #         ce
                #         for ce in new_complex_events
                #         if ce.identifier.split(' = ')[0] == 'videoAndObjDet' and ce.probability == max_prob
                #     ]
                # )

    def terminate_output(self, *args, **kwargs):
        pass
