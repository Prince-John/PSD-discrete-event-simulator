import simpy
from events import DownstreamEvent
from EventLogger import EventLogger  # Ensure this import path is correct based on your setup

class IdealDigitizer:
    def __init__(self, env, logger, unitID):
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

    def process_event(self, downstream_event: DownstreamEvent, debug=False):
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


if __name__ == '__main__':
    env = simpy.Environment()
    logger = EventLogger('digitizer_log.csv', env)
    digitizer = IdealDigitizer(env, logger, "DGT-001")

    # Sample DownstreamEvent for testing
    test_event = DownstreamEvent(simpy.Event(env),{'event_number': '001'}, {'info': 'Test Event 1'})

    # Process the event in the simulation
    env.process(digitizer.process_event(test_event, debug=True))
    env.run()
    logger.close()
