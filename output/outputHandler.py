from output.audio import Audio
from output.graph import initialize_graph
from output.sue import initialize_sue_connection
from output.text import Text
from output.timings import Timings
from output.video import Video
from output.connection_output.zmqconnection import ZMQConnection


class OutputHandler(object):
    def __init__(self, input_feed, event_generator, expected_events_list, event_definition, add_to_model, max_window,
                 cep_frequency, group_size, group_frequency, graph_x_size, fps, precompile, text, clean_text, timings,
                 use_graph, play_audio, audio_file, play_video, video_name, video_x_position, video_y_position, loop_at,
                 button, post_message, zmq_address, zmq_port, ce_threshold, video_scale, mark_objects, save_graph_to,
                 sue_address):
        self.outputs = []

        if timings:
            self.outputs.append(Timings())

        if text:
            self.outputs.append(Text())

        graph = initialize_graph(
            use_graph, graph_x_size, input_feed, expected_events_list, ce_threshold, save_graph_to
        )
        if graph:
            self.outputs.append(graph)

        if play_video:
            self.outputs.append(Video(video_x_position, video_y_position, video_scale, video_name, mark_objects))

        if zmq_address:
            self.outputs.append(ZMQConnection(zmq_address, zmq_port))

        sue_connection = initialize_sue_connection(sue_address)
        if sue_connection:
            self.outputs.append(sue_connection)

        if play_audio:
            self.outputs.append(Audio(audio_file))

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
