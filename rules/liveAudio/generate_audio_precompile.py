from anomalyDetection.audio.generate_audio_precompile import generate_precompile_file

if __name__ == '__main__':
    generate_precompile_file(
        complex_event_list=[
            'ceSilence',
            'ceSpeech',
        ],
        input_clauses_list=[
            'silence',
            'speech',
        ],
        window=10,
        output_filename='precompile_args.json'
    )
