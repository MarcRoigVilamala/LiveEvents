from output.audio import Audio
from output.graph import Graph
from output.sue import initialize_sue_connection
from output.text import Text
from output.timings import Timings
from output.video import Video
from output.connection_output.zmqconnection import ZMQConnection


class OutputHandler(object):
    def __init__(self, input_feed, expected_events_list, conf):
        self.outputs = []

        if conf['output'].get('timings'):
            self.outputs.append(Timings())

        if conf['output'].get('text'):
            self.outputs.append(Text())

        graph_conf = conf['output'].get('graph')
        if graph_conf and (graph_conf.get('use_graph') or graph_conf.get('save_graph_to')):
            self.outputs.append(
                Graph(
                    graph_conf.get('graph_x_size') or input_feed.get_max_length(),
                    expected_events_list,
                    conf['events']['ce_threshold'],
                    graph_conf.get('save_graph_to', False),
                    use_rectangles=False
                )
            )

        video_conf = conf['output'].get('video')
        if video_conf and video_conf.get('play_video'):
            self.outputs.append(
                Video(
                    video_conf.get('video_x_position', 1000),
                    video_conf.get('video_y_position', 200),
                    video_conf.get('video_scale', 1.0),
                    conf['input']['video_name'],
                    video_conf.get('mark_objects', False)
                )
            )

        zmq_conf = conf['output'].get('zmq_address')
        if zmq_conf:
            self.outputs.append(ZMQConnection(zmq_conf['zmq_address'], zmq_conf['zmq_port']))

        sue_connection = initialize_sue_connection(conf['output'].get('sue_address'))
        if sue_connection:
            self.outputs.append(sue_connection)

        if conf['output'].get('play_audio'):
            self.outputs.append(Audio(conf['input']['audio_file']))

    def finish_initialization(self):
        for o in self.outputs:
            o.finish_initialization()

    def update(self, output_update):
        for o in self.outputs:
            o.update(output_update)

    def terminate_outputs(self, evaluation):
        for o in self.outputs:
            o.terminate_output(
                evaluation=evaluation
            )
