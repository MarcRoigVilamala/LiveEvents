import json


def check_conf_format(conf):
    # TODO: Check interior values

    return 'input' in conf and 'output' in conf and 'events' in conf and 'misc' in conf


def parse_configuration(conf_filename):
    with open(conf_filename, 'r') as f:
        conf = json.load(f)

    assert check_conf_format(conf)

    return conf


def create_configuration(tracked_ce, event_definition, input_feed_type, add_to_model, add_event_generator,
                         audio_file, max_window, cep_frequency, group_size, group_frequency, graph_x_size,
                         interesting_objects, fps, precompile, text, clean_text, timings, use_graph, play_audio,
                         play_video, video_name, video_x_position, video_y_position, loop_at, button, post_message,
                         zmq_address, zmq_port, ce_threshold, video_scale, mark_objects, save_graph_to, sue_address):
    conf = {
        'input': {
            'input_feed_type': input_feed_type,
            'add_event_generator': add_event_generator,
            'interesting_objects': interesting_objects,
            'audio_file': audio_file,
            'video_name': video_name,
            'loop_at': loop_at,
            'button': button,
            'post_message': post_message
        },
        'output': {
            'text': text,
            'clean_text': clean_text,
            'timings': timings,
            'graph': {
                'use_graph': use_graph,
                'graph_x_size': graph_x_size,
                'save_graph_to': save_graph_to
            } if use_graph else {},
            'video': {
                'play_video': play_video,
                'video_x_position': video_x_position,
                'video_y_position': video_y_position,
                'video_scale': video_scale,
                'mark_objects': mark_objects
            } if play_video else {},
            'play_audio': play_audio,
            'zmq': {
                'zmq_address': zmq_address,
                'zmq_port': zmq_port
            } if zmq_address else {},
            'sue_address': sue_address
        },
        'events': {
            'tracked_ce': tracked_ce,
            'event_definition': event_definition,
            'add_to_model': add_to_model,
            'ce_threshold': ce_threshold
        },
        'logic': {
            'max_window': max_window,
            'cep_frequency': cep_frequency,
            'group_size': group_size,
            'group_frequency': group_frequency,
            'precompile': precompile
        },
        'misc': {
            'fps': fps
        }
    }

    assert check_conf_format(conf)

    return conf


def update_configuration_values(conf, *args, **kwargs):
    update_with = remove_empty_values(create_configuration(*args, **kwargs))

    for general_key, general_value in conf.items():
        for update_key, update_value in update_with[general_key].items():
            conf[general_key][update_key] = update_value

    conf = remove_empty_values(conf)

    assert check_conf_format(conf)

    return conf


def remove_empty_values(conf):
    assert check_conf_format(conf)

    new_conf = {
        general_key: {
            subkey: value
            for subkey, value in general_value.items()
            if value
        }
        for general_key, general_value in conf.items()
    }

    assert check_conf_format(new_conf)

    return new_conf


def save_configuration(conf, conf_filename):
    assert check_conf_format(conf)

    with open(conf_filename, 'w') as f:
        json.dump(conf, f, indent=4)
