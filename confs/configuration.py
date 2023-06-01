import json

# Use / to define keys for the sub-dictionaries
import sys

REQUIRED_FIELDS = [
    'input',
    'output',
    'events',
    'logic',
    'misc',
    'input/input_feed',
    'input/input_feed/type',
    'input/event_generators',
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
                         sue_address, cogni_sketch_url, cogni_sketch_project, cogni_sketch_project_owner,
                         cogni_sketch_user, cogni_sketch_password, cogni_sketch_use_simplified_explanations,
                         evaluatable, explanation, simple_events_text):
    conf = {
        'input': {
            'input_feed': {
                'type': input_feed_type,
                'audio_file': audio_file,
                'video_name': video_name,
            },
            'event_generators': [
                {
                    'type': event_generator,
                    'interesting_objects': interesting_objects,
                }
                for event_generator in add_event_generator
            ],
            'loop_at': loop_at,
            'button': button,
            'post_message': post_message
        },
        'output': {
            'text': text,
            'clean_text': clean_text,
            'explanation': explanation,
            'simple_events_text': simple_events_text,
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
            'sue_address': sue_address,
            'cogni_sketch': {
                "url": cogni_sketch_url,
                "project": cogni_sketch_project,
                "project_owner": cogni_sketch_project_owner,
                "user": cogni_sketch_user,
                "password": cogni_sketch_password,
                "use_simplified_explanations": cogni_sketch_use_simplified_explanations
            } if cogni_sketch_url else {}
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
            'precompile': precompile,
            'evaluatable': evaluatable
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
        for update_key, update_value in update_with.get(general_key, {}).items():
            conf[general_key][update_key] = update_value

    return conf


def remove_empty_values(conf):
    # Recursively removes all values evaluated as false (including None and empty dictionaries) from the conf

    new_conf = {}
    for k, v in conf.items():
        if isinstance(v, dict):
            v = remove_empty_values(v)

        if v:
            new_conf[k] = v

    return new_conf


def save_configuration(conf, conf_filename):
    assert check_conf_format(conf)

    # Ensure that the configuration will not be overwritten every time by not saving the "save_conf_as" parameter
    if 'save_conf_as' in conf['misc']:
        del conf['misc']['save_conf_as']

    with open(conf_filename, 'w') as f:
        json.dump(conf, f, indent=4)
