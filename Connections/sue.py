import os

import websockets
import asyncio
import json
from shutil import copyfile


class SUEConnection(object):
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
