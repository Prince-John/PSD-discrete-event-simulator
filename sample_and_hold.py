import simpy
import itertools
import numpy as np


def sample_and_hold_unit(env, sample_length, unit_index, debug=False):
    """
    A simple Sample and Hold unit simulation.
    NOTE:  if the `sample_length` is shorter than the integration delay this model fails.
    Currently, the propagation through each S&H is what simulates the integrator sampling things.


    :param env: simpy environment
    :param sample_length: amount of time taken for the sample, this is depended on the integrator delay.
    :param unit_index: accounting variable, used to show where in the chain of S&H units is this located.
    :param debug: Boolean flag for printing debug messages, default = `False`
    :return:
    """
    if debug: print(f"At s&h unit {unit_index}, starting processing at time {env.now}.")
    yield env.timeout(sample_length)
    if debug: print(f"At s&h unit {unit_index}, completed processing at time {env.now}.")


def ring_buffer(env, buffer_length, sample_length, chain_delay_overhead=0, debug=False):
    """
    Creates a ring delay buffer by chaining sample and hold units.

    :param env: simpy environment
    :param buffer_length: number of chained S&H units
    :param sample_length: amount of time taken per sample unit
    :param chain_delay_overhead: parameterized delay associated with parasitics of chaining S&H units
    :param debug: Boolean flag for printing debug messages, default = `False`
    :return:
    """
    for i in range(buffer_length):
        yield env.process(sample_and_hold_unit(env, sample_length, i, debug))
        if debug: print(f"Chaining delay introduced after s&h unit {i} at time {env.now}.")
        yield env.timeout(chain_delay_overhead)  # Adding chaining delay overhead
