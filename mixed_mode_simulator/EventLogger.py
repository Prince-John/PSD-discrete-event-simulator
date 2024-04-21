from events import DetectionEvent, DownstreamEvent
import simpy
import csv
import os  # Import os module to handle file directory operations

class EventLogger:
    def __init__(self, filename, env):
        self.env = env
        # Ensure the 'data' directory exists
        self.directory = 'data'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        # Define the full path for the CSV file
        self.full_path = os.path.join(self.directory, filename)
        # Open the file in write mode
        self.file = open(self.full_path, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['eventID', 'state@end', 'failure location(locationIndex/ID)', 'eventSuccessValue'])
        self.lock = simpy.Resource(env, capacity=1)

    def log_event(self, component, unit_index, downstream_event: DownstreamEvent):
        """
        Log an event to the CSV file using the DownstreamEvent object which contains
        a SimPy Event and related event information.

        :param component: Component involved in the event
        :param unit_index: Index or ID of the unit
        :param downstream_event: The downstream event being logged
        """
        with self.lock.request() as req:
            yield req
            event_id = downstream_event.detection_event_info['event_number']
            state_at_end = downstream_event.event.triggered  # Assuming 'event' in DownstreamEvent is a SimPy Event
            failure_location = f"{component}{unit_index}"
            event_success_value = 1  # Placeholder, can be changed as required

            self.writer.writerow([event_id, state_at_end, failure_location, event_success_value])
    
    def close(self):
        """ Close the file """
        self.file.close()

def sample_and_hold_unit(env, sample_length, unit_index, logger, detection_event, debug=False):
    if debug: print(f"At s&h unit {unit_index}, starting processing at time {env.now}.")
    sim_event = simpy.Event(env)  # Create a new SimPy event for downstream processing
    downstream_event = DownstreamEvent(sim_event, detection_event.event_info, {"unit_process": "sample_and_hold"})
    yield env.timeout(sample_length)
    sim_event.succeed()  # Mark the event as processed
    if debug: print(f"At s&h unit {unit_index}, completed processing at time {env.now}.")
    yield from logger.log_event('Sample_and_Hold', unit_index, downstream_event)

def ring_buffer(env, buffer_length, sample_length, chain_delay_overhead, logger, debug=False):
    for i in range(buffer_length):
        # Create a detection event for each unit in the buffer
        detection_event = DetectionEvent(simpy.Event(env), {"event_number": f"{i}", "info": "Event from Scintillator"})
        # Process each sample and hold unit
        yield env.process(sample_and_hold_unit(env, sample_length, i, logger, detection_event, debug))
        if debug:
            print(f"Chaining delay introduced after s&h unit {i} at time {env.now}.")
        # Log the chaining delay event
        delay_sim_event = simpy.Event(env)
        delay_downstream_event = DownstreamEvent(delay_sim_event, detection_event.event_info, {"unit_process": "chaining_delay"})
        yield env.timeout(chain_delay_overhead)
        delay_sim_event.succeed()  # Mark the delay event as processed
        yield from logger.log_event('ring_buffer', i, delay_downstream_event)

if __name__ == '__main__':
    env = simpy.Environment()
    logger = EventLogger('events_log1.csv', env)
    env.process(ring_buffer(env, 5, 1, 0.1, logger, debug=True))
    env.run(until=10)
    logger.close()
