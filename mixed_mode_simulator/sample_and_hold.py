import simpy
import itertools
import numpy as np
from .events import *


class AnalogBuffer:

    def __init__(self, env, buffer_index, buffer_location, sample_length, buffer_length, chain_delay, debug=False):
        """
        Creates an analog buffer with a parameterizable number of individual memory units and sample lengths.
        This class can be used to create both the long tail buffers and initial ring buffers.

        :param buffer_index: unique index count of the buffer in its respective location.
        :param buffer_location: String either "ring" or "tail" to determine the location of this buffer object
        :param env: simpy environment
        :param buffer_length: number of chained S&H units
        :param sample_length: amount of time taken per sample unit
        :param chain_delay: parameterized delay associated with parasitics of chaining S&H units
        :param debug: Boolean flag for printing debug messages, default = `False`

        """
        self.buffer_index = buffer_index
        self.buffer_location = buffer_location
        self.env = env
        self.sample_length = sample_length
        self.buffer_length = buffer_length
        self.chain_delay = chain_delay
        self.debug = debug

    def sample_and_hold_unit(self, event: DownstreamEvent, unit_index):
        """
        A single memory unit delay simulation

        :param event: DownstreamEvent object that carries event information.
        :param unit_index: accounting variable, used to show where in the chain of S&H units is this located.
        :return: None
        """
        if self.debug:
            print(f'At s&h unit {unit_index}, event {event.detection_event_info["event_number"]}, sample index '
                  f'{event.event_info["sample_index"]} starting processing '
                  f'at time {self.env.now}.')

        yield self.env.timeout(self.sample_length)

        if self.debug:
            print(f'At s&h unit {unit_index}, event {event.detection_event_info["event_number"]}, sample index '
                  f'{event.event_info["sample_index"]} finished processing '
                  f'at time {self.env.now}.')

    def remove_from_buffer(self, event: DownstreamEvent, mux):
        """
        This processes the removal and chaining of an event from a buffer to the next analog multiplexer. The
        AMUX will deal with the decision to either drop or accept this event. This function always offloads the event
        and keeps count of number of events removed.

        :param event: DownstreamEvent object that carries event information.
        :param mux: Multiplexer object that is used to chain the event.
        :return: None
        """
        pass

    def buffer(self, event: DownstreamEvent):
        """
        Creates an analog buffer by chaining sample and hold units.

        :param event: DownstreamEvent object that carries event information.
        :return: None
        """
        for i in range(self.buffer_length):
            yield self.env.process(self.sample_and_hold_unit(event, i))
            yield self.env.timeout(self.chain_delay)  # Adding chaining delay overhead

        self.remove_from_buffer(event, None)


