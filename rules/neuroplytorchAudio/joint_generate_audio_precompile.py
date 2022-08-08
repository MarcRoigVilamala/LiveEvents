from anomalyDetection.audio.generate_audio_precompile import generate_precompile_dict, save_precompile_file

if __name__ == '__main__':
    nplyt = generate_precompile_dict(
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
        event_type='neuroplytorchAudio'
    )

    dp = generate_precompile_dict(
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
        window=10
    )

    joint = {}
    for k in nplyt.keys():
        joint[k] = nplyt[k] + dp[k]

    save_precompile_file(joint, 'joint_precompile_args.json')
