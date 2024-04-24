from unittest import TestCase

import simpy
from mixed_mode_simulator import amux
from mixed_mode_simulator import events
from mixed_mode_simulator import sample_and_hold
import numpy as np

class TestAMUX(TestCase):

    def setUp(self) -> None:
        self.env = simpy.Environment()
        self.buffer_length = 5
        self.buffers = [sample_and_hold.AnalogBuffer(self.env, i, "tail", 1, self.buffer_length, 0, debug=True) for i
                        in range(3)]

        self.test_events = [events.DownstreamEvent(simpy.Event(self.env), {"event_number": 1, "scintillator": 1,
                                                                           "event_length": 1}, {"sample_index": i})
                            for i in range(10)]
        self.amux_delay = 0
        self.amuxID = 0
        self.Logger = event_logger.EventLogger('amux_testlog',self.env)
        self.mux = amux.AMUX(self.env, 3, self.buffers, self.amux_delay, self.Logger,self.amuxID,  debug=True)
        self.ring = [sample_and_hold.AnalogBuffer(self.env, i, "ring", 1, self.buffer_length, 0, debug=True) for i
                     in range(3)]
        for buf in self.ring:
            buf.set_amux(self.mux)

    def run_simulation_1_ring_1_tail(self, buffer_length, amux_delay, debug):
        self.env = simpy.Environment()
        tail_buffer = sample_and_hold.AnalogBuffer(self.env, 0, "tail", 1, buffer_length, 0, debug=debug)
        mux = amux.AMUX(self.env, 1, [tail_buffer], amux_delay, debug=debug)
        ring_buffer = sample_and_hold.AnalogBuffer(self.env, 0, "ring", 1, buffer_length, 0, debug=debug)
        ring_buffer.set_amux(mux)

        test_event = events.DownstreamEvent(simpy.Event(self.env), {"event_number": 1, "scintillator": 1,
                                                                    "event_length": 1}, {"sample_index": 0})

        self.env.process(ring_buffer.buffer(test_event))
        with self.assertRaises(Exception):
            self.env.run()

        self.assertEqual(self.env.now, buffer_length + amux_delay + buffer_length)

    def test_entry_base_case_1_ring_1_tail(self):
        """
             Base case with delay = 1 for all, buf_length =1
        """
        with self.subTest(buffer_length=1, amux_delay=1):
            self.run_simulation_1_ring_1_tail(1, 1, True)

    def test_entry_parameter_sweeps_1_ring_1_tail(self):
        """
              Iterates over desired parameter values and runs the simulation test for each.
              """
        buffer_lengths = [i for i in range(1, 10)]  # Example buffer lengths
        amux_delays = [i for i in np.logspace(-1, 2, 10)]  # Example amux delays

        for buffer_length in buffer_lengths:
            for amux_delay in amux_delays:
                with self.subTest(buffer_length=buffer_length, amux_delay=amux_delay):
                    self.run_simulation_1_ring_1_tail(buffer_length, amux_delay, False)

    def over_allocation_helper(self):

        tail_buffer = sample_and_hold.AnalogBuffer(self.env, 0, "tail", 1, 5, 0, debug=True)
        mux = amux.AMUX(self.env, 2, [tail_buffer], 0, debug=True)
        for buf in self.ring:
            buf.set_amux(mux)

        test_events = [events.DownstreamEvent(simpy.Event(self.env), {"event_number": i, "scintillator": i,
                                                                      "event_length": 1}, {"sample_index": 0})
                       for i in range(4)]

        self.env.process(self.ring[1].buffer(test_events[1]))
        yield self.env.timeout(0.5)
        self.env.process(self.ring[0].buffer(test_events[0]))

    def test_over_allocation(self):

        self.env.process(self.over_allocation_helper())

        with self.assertRaises(Exception):
            self.env.run()

    def release_helper(self):

        ring = [sample_and_hold.AnalogBuffer(self.env, i, "ring", 1, 4, 0, debug=True) for i
                in range(3)]

        tail_buffer = sample_and_hold.AnalogBuffer(self.env, 0, "tail", 1, 100, 0, debug=True)
        mux = amux.AMUX(self.env, 2, [tail_buffer], 0, debug=True)
        for buf in ring:
            buf.set_amux(mux)

        test_events_0 = [events.DownstreamEvent(simpy.Event(self.env), {"event_number": i, "scintillator": i,
                                                                        "event_length": 1}, {"sample_index": 0}, False)
                         for i in range(4)]
        test_events_1 = [events.DownstreamEvent(simpy.Event(self.env), {"event_number": i, "scintillator": i,
                                                                        "event_length": 1}, {"sample_index": 1}, True)
                         for i in range(4)]

        for buf in ring:
            print(f'for ring {buf.buffer_index} AMUX is {buf.amux}')
        self.env.process(ring[1].buffer(test_events_0[1]))
        yield self.env.timeout(1)
        self.env.process(ring[1].buffer(test_events_1[1]))
        yield self.env.timeout(5)
        self.env.process(ring[0].buffer(test_events_0[0]))
        yield self.env.timeout(1)
        self.env.process(ring[0].buffer(test_events_1[0]))

    def test_release(self):
        self.env = simpy.Environment()
        self.env.process(self.release_helper())

        with self.assertRaises(Exception):
            self.env.run()
