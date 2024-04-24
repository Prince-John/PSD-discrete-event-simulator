import simpy
from events import DownstreamEvent
from event_logger import EventLogger


class IdealDigitizer:
    def __init__(self, env, logger, unitID, debug=False):
        """
        Initializes the IdealDigitizer with an event logger and a unique identifier.
        Args:
            env (simpy.Environment): The simulation environment.
            logger (EventLogger): The logger to record event data.
            unitID (str): Unique identifier for the digitizer unit.
        """
        self.env = env
        self.logger = logger
        self.unitID = unitID  # Unique identifier for this digitizer
        self.debug = debug

    def buffer_in(self, downstream_event: DownstreamEvent, debug=False):
        """
        Processes a downstream event, marks it as successful, and logs the event.
        Args:
            downstream_event (DownstreamEvent): The event being processed.
            debug (bool): If True, prints debug information.
        """
        # Assume all events processed by this ideal digitizer are successful
        downstream_event.event.succeed()  # Mark the SimPy event as succeeded
        if self.debug:
            print(
                f"{self.env.now:.3f}\tEvent successfully received: {downstream_event.detection_event_info}")  # Debug message

        # Log the event processing success
        yield self.env.process(self.logger.log_event('Digitizer', self.unitID, downstream_event))


