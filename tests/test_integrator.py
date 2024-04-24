import math
import unittest

import numpy as np
import simpy
from mixed_mode_simulator import events
from mixed_mode_simulator import sample_and_hold
from mixed_mode_simulator import integrator


class IntegratorTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.DEBUG = False
        self.env = simpy.Environment()
        self.sample_length = 1
        self.test_ring = sample_and_hold.AnalogBuffer(self.env, 1, "ring-test", self.sample_length, 1, 0, self.DEBUG)

        self.integrator = integrator.Integrator(self.env, self.test_ring, 0, 0, self.sample_length)

    def test_downstream_event_count(self, event_length=10, sample_length=1):
        """ Test if the correct number of downstream events are being generated given a test Detection Event."""

        test_event = events.DetectionEvent(simpy.Event(self.env),
                                           event_info={"event_number": 0,
                                                       "scintillator": 0, "event_length": event_length})

        test_ring = sample_and_hold.AnalogBuffer(self.env, 1, "ring-test", sample_length, 1, 0, self.DEBUG)
        integrator_test = integrator.Integrator(self.env, test_ring, 0, 0, sample_length, debug=False)

        self.env.process(integrator_test.process_event(test_event))
        self.env.run()
        self.assertEqual((math.ceil(event_length / sample_length)), test_ring.downstream_events_processed)
        self.assertEqual(integrator_test.downstream_events_created, test_ring.downstream_events_processed)

        # add assertion here

    def test_downstream_event_count_sweep(self):

        event_lengths = np.logspace(-2, 1, num=10)
        sample_lengths = np.logspace(-3, 1, num=10)

        for event_length in event_lengths:
            for sample_length in sample_lengths:
                with self.subTest(event_length=event_length, sample_length=sample_length):
                    self.test_downstream_event_count(event_length, sample_length)


if __name__ == '__main__':
    unittest.main()
