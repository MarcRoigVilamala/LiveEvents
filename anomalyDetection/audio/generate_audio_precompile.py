import json

COMPLEX_EVENTS = [
    "single",
    "chained",
    "training",
]

SOUNDS = [
    'boom',
    'siren',
    'silence',
    'gun_shot',
    'shatter',
    'screaming',
]


def make_input_clauses_with_event_type(sound_list, window, event_type='sound'):
    return [
        {
            'event': sound,
            'timestamp': i,
            'event_type': event_type
        }
        for sound in sound_list
        for i in range(window)
    ]


def make_input_clauses_from_complex_events(complex_event_list, window):
    return [
        {
            "timestamp": i,
            "event": "{}=true".format(ce),
            "event_type": "holdsAt_"
        }
        for ce in complex_event_list
        for i in range(window)
    ]


def make_queries(complex_event_list, window):
    return [
        {
            'identifier': ce,
            "timestamp": window
        }
        for ce in complex_event_list
    ]


def generate_precompile_dict(complex_event_list, input_clauses_list, window, event_type='sound'):
    return {
        'input_clauses':
            make_input_clauses_with_event_type(
                input_clauses_list, window, event_type=event_type
            ) + make_input_clauses_from_complex_events(
                complex_event_list, window
            ),
        "queries": make_queries(complex_event_list, window)
    }


def save_precompile_file(precomp_dict, output_filename):
    with open(output_filename, 'w') as f:
        json.dump(precomp_dict, f, indent=4)


def generate_precompile_file(complex_event_list, input_clauses_list, window, output_filename, event_type='sound'):
    res = generate_precompile_dict(complex_event_list, input_clauses_list, window, event_type=event_type)

    save_precompile_file(res, output_filename)


if __name__ == '__main__':
    generate_precompile_file(COMPLEX_EVENTS, SOUNDS, window=5, output_filename='audio_precompile_args.json')
