import json

from events import DetectionEvent, DownstreamEvent
import simpy
import csv
import os  # Import os module to handle file directory operations


class EventLogger:
    def __init__(self, filename, env, config, debug=False):
        self.config = config
        self.env = env
        # Ensure the 'data' directory exists
        self.directory = '../data'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        # Define the full path for the CSV file
        self.full_path = os.path.join(self.directory, filename)
        # Open the file in write mode
        self.file = open(self.full_path, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.lock = simpy.Resource(env, capacity=1)
        self.debug = debug

        self.write_configuration_parameters()

    def write_configuration_parameters(self):
        """
        Write the simulation configuration to the header of the file. Warning, assumes that the file is open already.
        """
        self.file.write(f'The system configuration is: \n{json.dumps(self.config, indent=4)}'
                        f'\n\nCSV FILE STARTS BELOW\n\n')
        self.writer.writerow(
            ['scintillatorID:eventID', 'state@end', 'failure location(locationIndex/ID)', 'eventSuccessValue('
                                                                                          'placeholder)'])

    def log_event(self, component, digitized, unit_index, downstream_event: DownstreamEvent):
        """
        Log an event to the CSV file using the DownstreamEvent object which contains
        a SimPy Event and related event information.

        :param component: Component involved in the event
        :param unit_index: Index or ID of the unit
        :param downstream_event: The downstream event being logged
        """
        if self.debug:
            print(f"{self.env.now * 1e6:.3f} us\t Logger Called by: {component}")

        with self.lock.request() as req:  # FOR ASYNCRONOUS LOGGING
            yield req  # FOR ASYNCRONOUS LOGGING
            event_id = f"{downstream_event.detection_event_info['scintillator']}:" \
                       f"{downstream_event.detection_event_info['event_number']}"
            state_at_end = digitized  # Assuming 'event' in DownstreamEvent is a SimPy Event
            failure_location = f"{component}{unit_index}"
            event_success_value = 1  # Placeholder, can be changed as required

            self.writer.writerow([event_id, state_at_end, failure_location, event_success_value])

    def close(self):
        """ Close the file """
        self.file.close()
