from anomalyDetection.audio.generate_audio_precompile import generate_precompile_file

if __name__ == '__main__':
    generate_precompile_file(
        complex_event_list=[
            'ceAirConditioner',
            'ceCarHorn',
            'ceChildrenPlaying',
            'ceDogBark',
            'ceDrilling',
            'ceEngineIdling',
            'ceGunShot',
            'ceJackhammer',
            'ceSiren',
            'ceStreetMusic',
            'ceWorryingSiren'
        ],
        input_clauses_list=[
            'airConditioner',
            'carHorn',
            'childrenPlaying',
            'dogBark',
            'drilling',
            'engineIdling',
            'gunShot',
            'jackhammer',
            'siren',
            'streetMusic'
        ],
        window=5,
        output_filename='worryingSiren_precompile_args.json'
    )
