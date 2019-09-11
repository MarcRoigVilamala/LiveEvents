import pickle

import zmq
from syncClock import now


class Connection(object):
    def __init__(self, address, port):
        context = zmq.Context.instance()

        self.socket = context.socket(zmq.PUB)
        self.socket.connect("tcp://{}:{}".format(address, port))
        # self.socket.bind("tcp://*:{}".format(port))

        # Initialize the connection for the timestamp
        now()

    def send(self, complex_events):
        for ce in complex_events:
            message = pickle.dumps(['fight', 'VIOLENCE', now(), ce.probability])

            self.socket.send_multipart(
                [
                    "{topic}".format(topic='VIOLENCE').encode(),
                    message
                ]
            )
