import os
import sys

import websockets
import asyncio
import json
from shutil import copyfile

from output.liveEventsOutupt import LiveEventsOutput


class SUEConnection(LiveEventsOutput):
    def __init__(self, uri, media_path='/home/marc/projectes/SUE/nodeJSON/media'):
        self.uri = uri
        self.media_path = media_path

    async def post(self, events):
        async with websockets.connect(self.uri) as websocket:
            message = {
                "type": "post",
                "events": events
            }

            await websocket.send(json.dumps(message))

    def post_to_sue(self, events):
        asyncio.get_event_loop().run_until_complete(self.post(events))

    def add_file_to_sue(self, path):
        filename = os.path.basename(path)

        copyfile(path, '{}/{}'.format(self.media_path, filename))

        return filename

    def finish_initialization(self):
        pass

    def update(self, output_update):
        pass

    def terminate_output(self, *args, **kwargs):
        sue_event = {
            "eventName": "DeepProbCEP Event",
            "eventType": "IED Attack",
            "description": "There is an explosion followed by silence",
            "sensorID": 264,
            "priority": 1,
            "datetime": "2020-03-04T16:11:00Z",
            "coordinates": [58.144672, 8.001553],
            "slctRevVideo": "bang_graph.mp4"
        }

        if self.graph and self.graph.save_graph_to:
            file_ref = self.sue_connection.add_file_to_sue(self.graph.save_graph_to)

            sue_event["slctRevVideo"] = file_ref

        self.post_to_sue([sue_event])


def initialize_sue_connection(sue_address):
    if sue_address:
        if SUEConnection is not None:
            sue_connection = SUEConnection(sue_address)
        else:
            print("SUE Connection could not be imported", file=sys.stderr)
            sue_connection = None
    else:
        sue_connection = None
    return sue_connection
