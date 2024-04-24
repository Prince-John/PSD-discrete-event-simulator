import argparse
import json
import sys
from datetime import datetime
import simpy

import digitizer
import sample_and_hold
import amux
import integrator
import scintillator
import event_logger

# Define the argument parser
parser = argparse.ArgumentParser(description='Simulation setup for signal processing')
# Configuration model design parameters
parser.add_argument('--num_SnH_ring_buff', type=int, help='Number of S&H units in ring buffers', default=None)
parser.add_argument('--num_channels', type=int, help='Number of front end channels', default=None)
parser.add_argument('--num_SnH_long_buff', type=int, help='Number of S&H units in long tail buffers', default=None)
parser.add_argument('--num_long_buffs', type=int, help='Number of long tail buffers', default=None)
parser.add_argument('--num_of_digitizers', type=int, help='Number of digitizers', default=None)
parser.add_argument('--amux_associativity', type=str, help='Description of how the AMUX connections can be routed. '
                                                           'TBD, currently not used.', default=None)

# Configuration model constants (with delays as floats)
parser.add_argument('--short_SnH_delay', type=float, help='Short S&H unit delay length', default=None)
parser.add_argument('--long_SnH_delay', type=float, help='Long S&H unit delay length', default=None)
parser.add_argument('--mux0_delay', type=float, help='Delay length introduced by the first MUX', default=0)
parser.add_argument('--mux1_delay', type=float, help='Delay length introduced by the second MUX', default=0)
parser.add_argument('--integrator_delay', type=float, help='Delay length of the integrator. This also sets the '
                                                           'granularity of the waveform resolution, since the gate '
                                                           'delays will be much shorter than the integrator delay, '
                                                           'this parameter combines both values.', default=0)
parser.add_argument('--mean_arrival_time', type=float, help='Mean arrival time for simulated events', default=None)
parser.add_argument('--scintillator_delay', type=float, help='Delay for the scintillator', default=None)
parser.add_argument('--min_time_over_threshold', type=float, help='Minimum time over threshold for scintillator '
                                                                  'detection', default=None)
parser.add_argument('--max_time_over_threshold', type=float, help='Maximum time over threshold for scintillator '
                                                                  'detection', default=None)
parser.add_argument('--num_of_events', type=int, help='Number of simulated events', default=None)

# Optional: Configuration file for overriding command line arguments
parser.add_argument('--config_file', type=str, help='Path to JSON config file', default="default_config.json")
parser.add_argument('--debug_log', type=bool, help='Generate and dump detailed debug logs to a debug_log.txt',
                    default=False)

# Parse the arguments
args = parser.parse_args()

# If a config file is specified, override the command line arguments with values from the config file
if args.config_file:
    try:
        with open(args.config_file, 'r') as f:
            config = json.load(f)
            for key, value in config.items():
                if hasattr(args, key):
                    setattr(args, key, value)
    except FileNotFoundError:
        print(f"Error: Config file {args.config_file} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the config file.")
        sys.exit(1)


# Test code to print the variables

def set_amux_for_all(mux: amux.AMUX, buffers: list) -> None:
    """
    Sets the AMUX pointer in each of the specified buffers to specified amux.

    """
    for buf in buffers:
        buf.set_amux(mux)


if __name__ == "__main__":
    DEBUG = args.debug_log

    print("Simulation Setup Variables:")
    print(json.dumps(config, indent=4))

    if DEBUG:
        sys.stdout = open('../data/debug_log.txt', 'w')
        print("Simulation Setup Variables:")
        print(json.dumps(config, indent=4))
        print("*" * 30, f'DEBUG LOG generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "*" * 30)

    env = simpy.Environment()
    logger = event_logger.EventLogger(f'events_log_{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', env)
    digitizers = [digitizer.IdealDigitizer(env, logger, i) for i in range(args.num_of_digitizers)]
    amux1 = amux.AMUX(env, args.num_long_buffs, digitizers, args.mux1_delay, debug=DEBUG)
    tail_buffers = [
        sample_and_hold.AnalogBuffer(env, buffer_index=i, buffer_location="tail", sample_length=args.long_SnH_delay,
                                     buffer_length=args.num_SnH_long_buff, chain_delay=0, debug=DEBUG) for i in
        range(args.num_long_buffs)]
    set_amux_for_all(amux1, tail_buffers)
    amux0 = amux.AMUX(env, logger=logger, channels=args.num_channels, downstream_buffers=tail_buffers,
                      amux_delay=args.mux0_delay, debug=DEBUG)
    ring_buffers = [
        sample_and_hold.AnalogBuffer(env, buffer_index=i, buffer_location="ring", sample_length=args.short_SnH_delay,
                                     buffer_length=args.num_SnH_ring_buff, chain_delay=0, debug=DEBUG) for i in
        range(args.num_channels)]
    set_amux_for_all(amux0, ring_buffers)
    integrators = [
        integrator.Integrator(env, ring_buffers[i], i, args.integrator_delay, sample_length=args.short_SnH_delay,
                              debug=DEBUG) for i
        in range(args.num_channels)]
    detectors = [
        scintillator.Scintillator(env, args.mean_arrival_time, args.scintillator_delay, args.min_time_over_threshold,
                                  args.max_time_over_threshold, args.num_of_events, i, integrators[i], debug=DEBUG)
        for i in range(args.num_channels)]

    for detector in detectors:
        detector.start_scintillator()

    env.run()
    if DEBUG:
        sys.stdout.close()
