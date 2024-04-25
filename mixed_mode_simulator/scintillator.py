import simpy
import numpy as np
from events import DetectionEvent
from integrator import Integrator


class Scintillator:
    def __init__(self, env, mean_arrival_time, scintillator_delay, min_time_over_threshold, max_time_over_threshold,
                 num_events, scintillator_index, integrator: Integrator, debug=False):

        self.max_event_length = min_time_over_threshold
        self.min_event_length = max_time_over_threshold
        self.debug = debug
        self.env = env
        self.mean_arrival_time = mean_arrival_time  # mean arrival time between any two events
        self.scintillator_delay = scintillator_delay  # time taken to notice event arrival in scintillator
        self.num_events = num_events  # total number of synthetic events
        self.scintillator_index = scintillator_index  # index of scintillator
        self.integrator = integrator  # Integrator object that connects this scintillator to the next integrator

    def generate_timing(self):
        """
        1. Generate array of arrival times of all events based on poisson distribution (numpy.random.poisson)
        2. Generate array of normally-distributed event length 

        output: two arrays

        """
        # Generate arrival times using Poisson distribution
        arrival_times = 1/np.random.poisson(self.mean_arrival_time, size=self.num_events)

        # Generate event lengths using a uniform distribution with cutoff points
        event_lengths = np.random.uniform(low=self.min_event_length, high=self.max_event_length, size=self.num_events)

        return arrival_times, event_lengths

    def generate_events(self):
        """
        1. Invoke a generate_timing() -> iterate through both arrays concurrently
        2. Look at arrival time, generate simpy event -> within event, message body: event #, scintillator #, event length
        3. pass event to integrator process
        4. timeout for arrival time of current event
        
        """
        arrival_times, event_lengths = self.generate_timing()
        if self.debug:
            print(
                f'{self.env.now*1e6:.3f} us\tFor Scintillator {self.scintillator_index}: Arrival times{arrival_times}, Event '
                f'Time over threshold {event_lengths}')

        for i in range(self.num_events):
            # Define event information
            new_event = DetectionEvent(simpy.Event(self.env),
                                       {"event_number": i, "scintillator": self.scintillator_index,
                                        "event_length": event_lengths[i]})

            # Schedule event with arrival time + scintillator delay
            if self.debug:
                print(f'{self.env.now*1e6:.3f} us\tEvent generated: {new_event.event_info}')

            yield self.env.timeout(arrival_times[i] + self.scintillator_delay)
            # Send event to integrator process
            self.env.process(self.integrator.process_event(new_event))

    def start_scintillator(self):
        """
        Starts the event generation process for the scintillator.
        """
        self.env.process(self.generate_events())


if __name__ == '__main__':
    env = simpy.Environment()

    # Create a scintillator object
    scintillator = Scintillator(env, 2, 0.5, 3, 15, 8)

    # Start the simulation
    scintillator.start_scintillator()
    env.run()
