from anomalyDetection.audio.generate_audio_precompile import generate_precompile_file

if __name__ == '__main__':
    generate_precompile_file(
        complex_event_list=[
            'ceNplytAirConditioner',
            'ceNplytCarHorn',
            'ceNplytChildrenPlaying',
            'ceNplytDogBark',
            'ceNplytDrilling',
            'ceNplytEngineIdling',
            'ceNplytGunShot',
            'ceNplytJackhammer',
            'ceNplytSiren',
            'ceNplytStreetMusic',
        ],
        input_clauses_list=[
            'outNplytAirConditioner',
            'outNplytCarHorn',
            'outNplytChildrenPlaying',
            'outNplytDogBark',
            'outNplytDrilling',
            'outNplytEngineIdling',
            'outNplytGunShot',
            'outNplytJackhammer',
            'outNplytSiren',
            'outNplytStreetMusic'
        ],
        window=3,
        output_filename='neuroplytorch_precompile_args.json',
        event_type='neuroplytorchAudio'
    )
