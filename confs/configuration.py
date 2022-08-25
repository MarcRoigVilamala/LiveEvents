import json

# Use / to define keys for the sub-dictionaries
import sys

REQUIRED_FIELDS = [
    'input',
    'output',
    'events',
    'logic',
    'misc',
    'input/input_feed_type',
    'input/add_event_generator',
    'events/tracked_ce',
    'events/event_definition',
    'events/ce_threshold',
    'logic/max_window',
    'logic/cep_frequency',
    'logic/group_size',
    'logic/group_frequency',
]


def check_conf_format(conf):
    missing = []

    for field in REQUIRED_FIELDS:
        keypath = field.split('/')

        current_dict = conf
        while keypath:
            key = keypath[0]
            if key not in current_dict:
                missing.append(
                    'The key {} is missing from the required field {}'.format(key, field)
                )
                break
            else:
                current_dict = current_dict[key]
                keypath = keypath[1:]

    if missing:
        for m in missing:
            print(m, file=sys.stderr)

        return False

    return True


def parse_configuration(conf_filename):
    with open(conf_filename, 'r') as f:
        conf = json.load(f)

    return conf


def create_configuration(save_conf_as, tracked_ce, event_definition, input_feed_type, use_framework,
                         add_event_generator, audio_file, max_window, cep_frequency, group_size, group_frequency,
                         graph_x_size, interesting_objects, fps, precompile, text, clean_text, timings, use_graph,
                         play_audio, play_video, video_name, video_x_position, video_y_position, loop_at, button,
                         post_message, zmq_address, zmq_port, ce_threshold, video_scale, mark_objects, save_graph_to,
                         sue_address):
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
            'use_framework': use_framework,
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
            'fps': fps,
            'save_conf_as': save_conf_as
        }
    }

    conf = remove_empty_values(conf)

    return conf


def update_configuration_values(conf, *args, **kwargs):
    update_with = create_configuration(*args, **kwargs)

    for general_key, general_value in conf.items():
        for update_key, update_value in update_with[general_key].items():
            conf[general_key][update_key] = update_value

    conf = remove_empty_values(conf)

    return conf


def remove_empty_values(conf):
    new_conf = {
        general_key: {
            subkey: value
            for subkey, value in general_value.items()
            if value
        }
        for general_key, general_value in conf.items()
    }

    return new_conf


def save_configuration(conf, conf_filename):
    assert check_conf_format(conf)

    # Ensure that the configuration will not be overwritten every time by not saving the "save_conf_as" parameter
    if 'save_conf_as' in conf['misc']:
        del conf['misc']['save_conf_as']

    with open(conf_filename, 'w') as f:
        json.dump(conf, f, indent=4)
