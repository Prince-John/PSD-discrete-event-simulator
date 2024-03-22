import simpy
import itertools

from pingpong import *
from sample_and_hold import *


def ring_buffer_process(env, message, buffer_length, sample_length):

    yield env.process(ring_buffer(env, buffer_length, sample_length, debug=True))
    print(f"Event Edge {message.data['edge']} of Wave {message.data['id']} through the ring buffer at time {env.now}")

    message.event.succeed()


if __name__ == '__main__':
    # Simulation parameters
    period = 5  # Period of the square wave
    duration = 30  # Total duration of the simulation
    delta = 1  # Processing time for ping_pong Integrator
    # Setup the simulation

    env = simpy.Environment()
    # Integrator process setup
    integrator_process = lambda env, message: ping_pong_integrator(env, message, delta)

    # Set up the square wave generator with an integrator process
    env.process(square_wave_generator(env, period, duration, integrator_process))

    env.run()
