import argparse
import json
import sys

# Define the argument parser
parser = argparse.ArgumentParser(description='Simulation setup for signal processing')
parser.add_argument('--sample_length', type=int, help='Sample length', default=None)
parser.add_argument('--ring_buffer_length', type=int, help='Ring buffer length', default=None)
parser.add_argument('--ring_buffer_size', type=int, help='Ring buffer size', default=None)
parser.add_argument('--ring_buffer_delay', type=int, help='Ring buffer delay', default=None)
parser.add_argument('--integrator_delay', type=int, help='Integrator delay', default=None)
parser.add_argument('--integrator_size', type=int, help='Integrator size', default=None)
parser.add_argument('--sh_delay', type=int, help='S&H delay', default=None)
parser.add_argument('--sh_size', type=int, help='S&H size', default=None)
parser.add_argument('--poisson_delta', type=float, help='Poisson delta', default=None)
parser.add_argument('--num_channels', type=int, help='Number of channels', default=None)
parser.add_argument('--long_short_ratio', type=float, help='Long short ratio', default=None)
parser.add_argument('--config_file', type=str, help='Path to JSON config file', default=None)

# Parse the command line arguments
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
if __name__ == "__main__":
    print("Simulation Setup Variables:")
    print(f"Sample Length: {args.sample_length}")
    print(f"Ring Buffer Length: {args.ring_buffer_length}")
    print(f"Ring Buffer Size: {args.ring_buffer_size}")
    print(f"Ring Buffer Delay: {args.ring_buffer_delay}")
    print(f"Integrator Delay: {args.integrator_delay}")
    print(f"Integrator Size: {args.integrator_size}")
    print(f"S&H Delay: {args.sh_delay}")
    print(f"S&H Size: {args.sh_size}")
    print(f"Poisson Delta: {args.poisson_delta}")
    print(f"Number of Channels: {args.num_channels}")
    print(f"Long Short Ratio: {args.long_short_ratio}")
