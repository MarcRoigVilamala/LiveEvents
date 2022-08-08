import torch

from input.eventGeneration.Neuroplytorch import basic_models, models
from input.eventGeneration.event import Event


def load_pretrained_model(num_primitive_events=10, output_size=10, window_size=10):
    reasoning_model = models.ReasoningModel(input_size=num_primitive_events, output_size=output_size)
    reasoning_model = reasoning_model.model
    reasoning_model.load_state_dict(
        torch.load('neuralNetworkWeights/Neuroplytorch/reasoning_model.pt')
    )

    perception_model = basic_models.FromVGGish(
        input_size=128, output_size=num_primitive_events
    )
    perception_model.load_state_dict(
        torch.load('neuralNetworkWeights/Neuroplytorch/perception_model.pt')
    )
    perception_model = models.PerceptionWindow(
        perception_model=perception_model, window_size=window_size, num_primitive_events=num_primitive_events,
        loss_str='MSELoss', lr=0.001
    )

    end_model = models.Neuroplytorch(
        reasoning_model=reasoning_model, window_size=window_size, num_primitive_events=num_primitive_events,
        perception_model=perception_model, loss_str='MSELoss', lr=0.001
    )

    return end_model


class FromAudioNeuroplytorch(object):
    def __init__(self, perception_classes, ce_classes, network):
        self.perception_classes = perception_classes
        self.ce_classes = ce_classes

        self.network = network

    def get_events(self, enumerated_frames):
        timestamps, vggish_tensors = zip(*enumerated_frames)

        perception_outputs, overall_outputs = self.network.forward(torch.stack(vggish_tensors).unsqueeze(0))

        perception_outputs = perception_outputs.squeeze().tolist()
        overall_outputs = overall_outputs.squeeze().tolist()

        events = [
            Event(
                timestamp=t,
                event=c,
                probability=p,
                event_type='sound'
            )
            for t, _, outputs_at_t in zip(*zip(*enumerated_frames), perception_outputs)
            for c, p in zip(self.perception_classes, outputs_at_t)
        ]

        neuroplytorch_events = [
            Event(
                timestamp=timestamps[-1],
                event=c,
                probability=min(max(o, 0.0), 1.0),  # Limit the values between 0.0 and 1.0
                event_type='neuroplytorchAudio'
            )
            for c, o in zip(self.ce_classes, overall_outputs)
        ]

        return events + neuroplytorch_events


def generate_audio_neuroplytorch_event_gen(num_primitive_events=10, output_size=10, window_size=10):
    model = load_pretrained_model(num_primitive_events, output_size, window_size)

    perception_classes = [
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
    ]
    ce_classes = list(map(lambda x: "outNplyt{}".format(x[:1].capitalize() + x[1:]), perception_classes))

    return FromAudioNeuroplytorch(perception_classes, ce_classes, model)
