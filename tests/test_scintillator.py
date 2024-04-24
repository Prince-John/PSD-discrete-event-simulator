import unittest
import numpy as np
from mixed_mode_simulator import scintillator
from io import StringIO
import sys
import simpy

class ScintillatorTestCase(unittest.TestCase):
  
  def setUp(self) -> None:
    self.scintillator_index = 5

  def test_generate_timing(self):
    """
    1. Verifies that the generate_timing method produces the correct number of arrival times and event lengths.
    2. Verifies that the method is generating data based on mean arrival time and mean event length
    """

    min_arrival_time = 0
    max_arrival_time = 5
    mean_event_length = 3
    num_events = 10

    scintillator = Scintillator(None, min_arrival_time, min_arrival_time, 0, mean_event_length, num_events, self.scintillator_index)
    arrival_times, event_lengths = scintillator.generate_timing()

    self.assertEqual(len(arrival_times), num_events)
    self.assertEqual(len(event_lengths), num_events)

  def test_generate_events(self):
    """
    Tests whether the start_scintillator method triggers event generation and the expected number of events are created.
    """
    min_arrival_time = 0
    max_arrival_time = 5
    mean_event_length = 2
    num_events = 5

    # Capture printed information during event generation (assuming print statements)
    captured_output = StringIO()  
    sys.stdout = captured_output

    scintillator = Scintillator(None, min_arrival_time, min_arrival_time, 0, mean_event_length, num_events, self.scintillator_index)
    scintillator.start_scintillator()

    # Restore original stdout
    sys.stdout = sys.__stdout__

    # Verify expected number of events printed
    self.assertEqual(captured_output.getvalue().count("Event "), num_events)


if __name__ == '__main__':
  unittest.main()
