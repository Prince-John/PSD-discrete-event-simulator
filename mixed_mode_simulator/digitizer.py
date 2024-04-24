import simpy
from events import DownstreamEvent
from event_logger import EventLogger


class IdealDigitizer:
    def __init__(self, env, logger, unitID, debug=True):
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
        self.buffer_index = unitID # TODO: Get a uniform interface definition for component IDs, this is a bodge for backword compatibility.

    def buffer_in(self, downstream_event: DownstreamEvent):
        """
        Processes a downstream event, marks it as successful, and logs the event.
        Args:
            downstream_event (DownstreamEvent): The event being processed.
            debug (bool): If True, prints debug information.
        """
        # Assume all events processed by this ideal digitizer are successful
        print(self.debug)
        if self.debug:
            print(
                f"{self.env.now:.3f}\tEvent successfully received: {downstream_event.detection_event_info}, final event: {downstream_event.final_event}")  # Debug message

        # Log the event processing success
        if downstream_event.final_event:
            yield self.env.process(self.logger.log_event('Digitizer', self.unitID, downstream_event))

        downstream_event.event.succeed()  # Mark the SimPy event as succeeded
