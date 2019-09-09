import zmq


class Connection(object):
    def __init__(self, address, port):
        context = zmq.Context.instance()

        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://{}:{}".format(address, port))
        # self.socket.bind("tcp://*:{}".format(port))

    def send(self, complex_events):
        for ce in complex_events:
            self.socket.send_multipart(
                [
                    "{topic}".format(topic='cam1-inference').encode(),
                    "{label}; {confidence}; {sensorId}; {timestamp}".format(
                        label=ce.identifier.split(' = ')[0],
                        confidence=ce.probability,
                        sensorId='1',
                        timestamp=ce.timestamp
                    ).encode()
                ]
            )
