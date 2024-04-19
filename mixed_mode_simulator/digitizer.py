# assuming ideal digiizer
# unlimited bandwidth
# unlimited sampling rate

# takes in any events, record whether events were successfully received, success message

# debug statements to print subsequent success messages
# dump all success full events at very end

# function that takes downstream event, marks as successful, record if it receives detection even

class IdealDigitizer:
  """
  Simulates an ideal digitizer with unlimited bandwidth and sampling rate.

  This is a simplified model for educational purposes and doesn't represent
  the limitations of real-world digitizers.
  """

  def __init__(self):
    self.successful_events = []

  def process_event(self, event):
    """
    Processes a downstream event and marks it as successful.

    Args:
        event: Any data representing the downstream event.
    """
    self.successful_events.append(event)
    print(f"Event successfully received: {event}")  # Debug message

  def dump_events(self):
    """
    Prints all successfully processed events.
    """
    print("Successful Events:")
    for event in self.successful_events:
      print(event)

# Example usage
digitizer = IdealDigitizer()
digitizer.process_event("Data sample 1")
digitizer.process_event("Detection event")
digitizer.dump_events()
