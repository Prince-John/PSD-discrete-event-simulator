import math

import simpy
import itertools
from events import *


class Integrator:

    def __init__(self, env, ring_buff_process, integrator_index, integrator_delay, sample_length):
        """
        Integrator model, creates an object to simulate the analog integrator delay that takes in an event from
        a detectors, reads the event length and dispatches `n` events downstream to the ring buffer.
        n = ceil(event_length/sample_length)

        :param env: shared simpy environment
        :param ring_buff_process: downstream simpy ring_buff process
        :param integrator_index: integrator id, starts at 0
        :param integrator_delay: delay modeling the gate/discharge delays for the integrator
        :param sample_length: length of downstream S&H units, determines number of events dispatched by the integrator
        """
        self.sample_length = sample_length
        self.integrator_delay = integrator_delay
        self.integrator_index = integrator_index
        self.env = env
        self.ring_buff_process = ring_buff_process

    def process_event(self, detected_event: DetectionEvent, debug = False):
        yield self.env.timeout(self.integrator_delay)

        event_length = detected_event.event_info["event_length"]
        downstream_events = math.ceil(event_length / self.sample_length)

        for downstream_event_index in range(downstream_events):
            new_sample_event = DownstreamEvent(simpy.Event(self.env), detected_event.event_info,
                                               {"sample_index": downstream_event_index})
            yield self.env.timeout(self.sample_length)
            yield self.env.process(self.ring_buff_process(new_sample_event))

            if debug:
                print(f'In Integrator {self.integrator_index} with processed sample {downstream_event_index} for event {detected_event.event_info["event_number"]}')

        detected_event.event.succeed(value=f'Detection Event {detected_event.event_info["event_number"]} completed')
