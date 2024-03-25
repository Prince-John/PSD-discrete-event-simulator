import simpy
import itertools
from message import Message
from single_channel_test import *

def square_wave_generator(env, period, duration, integrator_process):
    for i in itertools.count():
        if i * period >= duration:
            break
        event = simpy.Event(env)
        yield env.timeout(period / 2)
        env.process(integrator_process(env, Message({'id': i, 'edge': 'Rising'}, event)))
        yield event  # Wait for the integrator to process the rising edge
        event = simpy.Event(env)
        yield env.timeout(period / 2)
        env.process(integrator_process(env, Message({'id': i, 'edge': 'Falling'}, event)))
        yield event  # Wait for the integrator to process the falling edge


def ping_pong_integrator(env, message, delta):
    yield env.timeout(delta)
    print(f"Time {env.now}: Edge {message.data['edge']} of Wave {message.data['id']} processed.")
    #message.event.succeed()  # Signal that the message has been processed
    env.process(ring_buffer_process(env, message, 3, 1))


if __name__ == '__main__':
    env = simpy.Environment()
    period = 5
    duration = 30
    delta = 1

    # Integrator process setup
    integrator_process = lambda env, message: ping_pong_integrator(env, message, delta)

    # Set up the square wave generator with an integrator process
    env.process(square_wave_generator(env, period, duration, integrator_process))

    env.run()