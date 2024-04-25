import math

import simpy
import itertools
from events import *
from sample_and_hold import AnalogBuffer


class Integrator:

    def __init__(self, env: simpy.Environment, ring_buffer: AnalogBuffer, integrator_index: int, integrator_delay,
                 sample_length, debug=False):
        """
        Integrator model, creates an object to simulate the analog integrator delay that takes in an event from
        a detectors, reads the event length and dispatches `n` events downstream to the ring buffer.
        n = ceil(event_length/sample_length)

        :param env: shared simpy environment
        :param ring_buffer: downstream AnalogBuffer object
        :param integrator_index: integrator id, starts at 0
        :param integrator_delay: delay modeling the gate/discharge delays for the integrator
        :param sample_length: length of downstream S&H units, determines number of events dispatched by the integrator
        """
        self.debug = debug
        self.ring_buffer = ring_buffer
        self.sample_length = sample_length
        self.integrator_delay = integrator_delay
        self.integrator_index = integrator_index
        self.env = env
        self.downstream_events_created = 0

    def process_event(self, detected_event: DetectionEvent):
        yield self.env.timeout(self.integrator_delay)

        event_length = detected_event.event_info["event_length"]
        downstream_events = math.ceil(event_length / self.sample_length)

        for downstream_event_index in range(downstream_events):
            new_sample_event = DownstreamEvent(simpy.Event(self.env), detected_event.event_info,
                                               {"sample_index": downstream_event_index})

            yield self.env.timeout(self.sample_length)
            if self.debug:
                print(
                    f'{self.env.now*1e6:.3f} us\tIn Integrator {self.integrator_index} with processed sample {downstream_event_index} for event {detected_event.event_info["event_number"]}')

            self.downstream_events_created += 1
            self.env.process(self.ring_buffer.buffer_in(new_sample_event))

        # detected_event.event.succeed(value=f'Detection Event {detected_event.event_info["event_number"]} completed')
