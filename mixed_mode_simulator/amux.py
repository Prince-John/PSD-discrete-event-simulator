class SimulatedAMUX:
  def __init__(self, channels):
    self.channels = channels
    self.selected_channel = 0

  def select_channel(self, channel):
    if channel < 0 or channel >= len(self.channels):
      raise ValueError("Invalid channel number")
    self.selected_channel = channel

  def get_output(self):
    return self.channels[self.selected_channel]