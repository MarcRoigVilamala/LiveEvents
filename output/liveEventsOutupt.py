from abc import ABC, abstractmethod


class LiveEventsOutput(ABC):
    @abstractmethod
    def finish_initialization(self):
        pass

    @abstractmethod
    def update(self, output_update):
        pass

    @abstractmethod
    def terminate_output(self, evaluation):
        pass
