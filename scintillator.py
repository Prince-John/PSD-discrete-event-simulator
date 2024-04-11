import simpy
import numpy as np

class Scintillator:
    def __init__(self, env, mean_arrival_time, scintillator_delay, mean_event_length, num_events, scintillator_index):
        self.env = env
        self.mean_arrival_time = mean_arrival_time  # mean arrival time between any two events
        self.scintillator_delay = scintillator_delay # time taken to notice event arrival in scintillator
        self.mean_event_length = mean_event_length # mean length of a single event
        self.num_events = num_events # total number of synthetic events 
        self.scintillator_index = scintillator_index # index of scintillator

    def generate_timing(self):
        """
        1. Generate array of arrival times of all events based on poisson distribution (numpy.random.poisson)
        2. Generate array of normally-distributed event length 

        output: two arrays

        """
        # Generate arrival times using Poisson distribution
        arrival_times = np.random.poisson(self.mean_arrival_time, size=self.num_events)

        # Generate event lengths from normal distribution
        event_lengths = np.random.normal(self.mean_event_length, scale=self.mean_event_length / 2, size=self.num_events)  # Adjust scale for desired standard deviation
        
        return arrival_times, event_lengths

    def generate_events(self):
        """
        1. Invoke a generate_timing() -> iterate through both arrays concurrently
        2. Look at arrival time, generate simpy event -> within event, message body: event #, scintillator #, event length
        3. pass event to integrator process
        4. timeout for arrival time of current event
        
        """        
        arrival_times, event_lengths = self.generate_timing()
        for i in range(self.num_events):
            # Define event information 
            event_info = {"event_number": i + 1, "scintillator": self.scintillator_index, "event_length": event_lengths[i]}
            # Schedule event with arrival time + scintillator delay
            yield self.env.timeout(arrival_times[i] + self.scintillator_delay)
            # Send event to integrator process
            self.env.process(self.integrator_process(event_info))

    def start_scintillator(self):
        """
        Starts the event generation process for the scintillator.
        """
        self.env.process(self.generate_events())

    def integrator_process(self, event_info):
        try:
            # print details of event detected
            print(f"Event {event_info['event_number']} detected in scintillator {event_info['scintillator']} with length {event_info['event_length']:.2f}")

            yield self.env.timeout(1)  
        except Exception as e:
            print(f"An error occurred: {e}") 

    
# Setup the simulation
env = simpy.Environment()

# Create a scintillator object
scintillator = Scintillator(env, 2, 0.5, 3, 15, 8)

# Start the simulation
scintillator.start_scintillator()
env.run()
