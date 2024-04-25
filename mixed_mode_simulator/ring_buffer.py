import simpy
from events import DetectionEvent, DownstreamEvent
from EventLogger import EventLogger

class RingBuffer:
    def __init__(self, env, buffer_length, sample_length, chain_delay_overhead, logger, unitID, debug=False):
        """
        Initializes the RingBuffer component.
        Args:
            env (simpy.Environment): The simulation environment.
            buffer_length (int): The number of units in the buffer.
            sample_length (float): The time each unit processes a sample.
            chain_delay_overhead (float): The delay introduced after processing each unit.
            logger (EventLogger): The logger to record event data.
            unitID (str): Unique identifier for the ring buffer.
            debug (bool): If True, prints debug information.
        """
        self.env = env
        self.buffer_length = buffer_length
        self.sample_length = sample_length
        self.chain_delay_overhead = chain_delay_overhead
        self.logger = logger
        self.unitID = unitID
        self.debug = debug

    def sample_and_hold_unit(self, unit_index, detection_event):
        if self.debug:
            print(f"At s&h unit {unit_index}, starting processing at time {self.env.now}.")
        sim_event = simpy.Event(self.env)  # Create a new SimPy event for downstream processing
        downstream_event = DownstreamEvent(sim_event, detection_event.event_info, {"unit_process": "sample_and_hold"})
        yield self.env.timeout(self.sample_length)
        sim_event.succeed()  # Mark the event as processed
        if self.debug:
            print(f"At s&h unit {unit_index}, completed processing at time {self.env.now}.")
        yield from self.logger.log_event('Sample_and_Hold', False, self.unitID + str(unit_index), downstream_event)

    def run(self):
        for i in range(self.buffer_length):
            # Create a detection event for each unit in the buffer
            detection_event = DetectionEvent(simpy.Event(self.env), {"event_number": f"{i}", "info": "Event from Scintillator"})
            # Process each sample and hold unit
            yield self.env.process(self.sample_and_hold_unit(i, detection_event))
            if self.debug:
                print(f"Chaining delay introduced after s&h unit {i} at time {self.env.now}.")
            # Log the chaining delay event
            delay_sim_event = simpy.Event(self.env)
            delay_downstream_event = DownstreamEvent(delay_sim_event, detection_event.event_info, {"unit_process": "chaining_delay"})
            yield self.env.timeout(self.chain_delay_overhead)
            delay_sim_event.succeed()  # Mark the delay event as processed
            yield from self.logger.log_event('Ring_Buffer', False, self.unitID + str(i), delay_downstream_event)

if __name__ == '__main__':
    env = simpy.Environment()
    logger = EventLogger('events_log1.csv', env)
    ring_buffer = RingBuffer(env, 5, 1, 0.1, logger, "RB-", debug=True)
    env.process(ring_buffer.run())
    env.run(until=10)
    logger.close()
