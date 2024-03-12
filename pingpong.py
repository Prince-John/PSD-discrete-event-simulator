import simpy
import itertools

def square_wave_generator(env, integrator, period, duration):
    """Generate a square wave with a given period and duration."""
    for i in itertools.count():
        if i * period >= duration:
            break  # Stop generating after reaching the simulation duration
        yield env.timeout(period / 2)  # High part of the square wave
        env.process(integrator(env, i, 'Rising'))
        yield env.timeout(period / 2)  # Low part of the square wave
        env.process(integrator(env, i, 'Falling'))

def ping_pong_integrator(env, id, edge,delta):
    """Process the square wave's edges with a delay."""
    processing_time = delta  # Adjust this processing time as needed
    yield env.timeout(processing_time)
    print(f"Time {env.now}: Edge {edge} of Wave {id} processed.")

# Simulation parameters
period = 5  # Period of the square wave
duration = 30  # Total duration of the simulation
delta = 1   # Processing time for ping_pong Integrator
# Setup the simulation
env = simpy.Environment()
integrator_process = lambda env, id, edge: ping_pong_integrator(env, id, edge,delta)
env.process(square_wave_generator(env, integrator_process, period, duration))

# Run the simulation
env.run()