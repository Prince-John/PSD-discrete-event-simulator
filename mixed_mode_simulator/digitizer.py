import simpy
from events import DownstreamEvent
#from event_logger import EventLogger  # Ensure this import path is correct based on your setup


class IdealDigitizer:
    def __init__(self, env, logger, unitID):
        """
        Initializes the IdealDigitizer with an event logger and a unique identifier.
        Args:
            env (simpy.Environment): The simulation environment.
            logger (EventLogger): The logger to record event data.
            unitID (int): Unique identifier for the digitizer unit.
        """
        self.env = env
        self.logger = logger
        self.unitID = unitID  # Unique identifier for this digitizer

    def process_event(self, downstream_event: DownstreamEvent, debug=True):
        """
        Processes a downstream event, marks it as successful, and logs the event.
        Args:
            downstream_event (DownstreamEvent): The event being processed.
            debug (bool): If True, prints debug information.
        """
        # Assume all events processed by this ideal digitizer are successful
        downstream_event.event.succeed()  # Mark the SimPy event as succeeded
        if debug:
            print(f"Event successfully received: {downstream_event.detection_event_info}")  # Debug message

        # Log the event processing success
        yield self.env.process(self.logger.log_event(
            'Digitizer',  # Component name
            self.unitID,  # Unit index, now using the unique identifier
            downstream_event
        ))

