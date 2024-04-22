import unittest
import IdealDigitizer

class DigitizerTestCase(unittest.TestCase):

  def setUp(self) -> None:
    self.digitizer = IdealDigitizer()

  def test_single_event(self):
    """
    Tests processing a single event.
    """
    test_event = "Test data"
    self.digitizer.process_event(test_event)
    self.assertEqual(len(self.digitizer.successful_events), 1)
    self.assertEqual(self.digitizer.successful_events[0], test_event)

  def test_multiple_events(self):
    """
    Tests processing multiple events.
    """
    events = ["Event 1", "Event 2", "Event 3"]
    for event in events:
      self.digitizer.process_event(event)
    self.assertEqual(len(self.digitizer.successful_events), len(events))
    for i, event in enumerate(events):
      self.assertEqual(self.digitizer.successful_events[i], event)

  def test_dump_events(self):
    """
    Tests the dump_events method.
    """
    test_event = "Sample data"
    self.digitizer.process_event(test_event)
    captured_output = StringIO()  # Capture printed output
    sys.stdout = captured_output
    self.digitizer.dump_events()
    sys.stdout = sys.__stdout__  # Restore original stdout
    self.assertIn(f"Event successfully received: {test_event}", captured_output.getvalue())

if __name__ == '__main__':
  unittest.main()