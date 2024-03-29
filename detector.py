import simpy
import random
import numpy as np


# Define simulation constants (adjust these values as needed)
PERIOD = 10  # ns (Time between particle interactions)
DURATION = 1000  # ns (Total simulation duration)
SCINTILLATION_YIELD = 10000  # Average photons per event (lambda for Poisson distribution)
EMISSION_TIME_CONSTANT = 10  # ns (exponential decay for prompt photons)


def scintillator(env):
    """
    Simulates photon generation in the scintillator using Poisson distribution.

    Args:
        env (simpy.Environment): SimPy environment object

    Yields:
        list: List of dictionaries containing photon information
    """

    # Generate number of photons based on Poisson distribution
    num_photons = np.random.poisson(SCINTILLATION_YIELD)

    photons = []
    for _ in range(num_photons):
        # Simulate prompt photon emission time (exponential decay)
        emission_time = yield env.timeout(np.random.exponential(EMISSION_TIME_CONSTANT))

        # Add information for each photon
        photon = {"arrival_time": emission_time, "wavelength": random.uniform(400, 500)}  # Example wavelength range
        photons.append(photon)

    yield env.timeout(0)  # Optional delay to simulate processing time
    return photons


def photomultiplier(env, arrival_time):
    """
    Simulates photomultiplier tube (PMT) response to photons.

    Args:
        env (simpy.Environment): SimPy environment object
        arrival_time (list): List of arrival times for photons

    Yields:
        list: List of timestamps for detected photons or None
    """

    detected_photons = []
    # Simulate detection probability (adjust this value)
    detection_probability = 0.8

    for time in arrival_time:
        if random.random() < detection_probability:
            detected_photons.append(env.timeout(time))  # Yield with photon arrival time

    yield env.timeout(0)  # Optional delay to simulate processing time
    return detected_photons if detected_photons else None


def preamp(env, signal):
    """
    Simulates preamplifier amplification and noise addition.

    Args:
        env (simpy.Environment): SimPy environment object
        signal (list): List of timestamps for detected photons (from PMT)

    Yields:
        list: Amplified and noisy signal
    """

    amplified_signal = []
    # Simulate amplification gain (adjust this value)
    gain = 100

    # Add noise (example: random jitter)
    jitter = np.random.normal(scale=0.5, size=len(signal))  # Adjust noise parameters

    for index, time in enumerate(signal):
        # Simulate processing time for each photon
        yield env.timeout(0.1)  # Adjust processing time

        # Apply gain and jitter
        amplified_signal.append(time * gain + jitter[index])

    yield env.timeout(0)  # Optional delay to simulate overall processing time
    return amplified_signal


def main():
    """
    Main function to run the simulation.
    """

    env = simpy.Environment()

    # Schedule particle interactions with the period
    while True:
        yield env.timeout(PERIOD)
        # Simulate particle interaction and detector response (replace with your logic)
        photons = scintillator(env)
        detected_photons = photomultiplier(env, [p["arrival_time"] for p in photons])
        if detected_photons:
            amplified_signal = preamp(env, detected_photons)
            # Process and analyze the amplified signal (replace with your analysis logic)
            print("Particle detected! Analyzing signal...")

        # Check if simulation duration is exceeded
        if env.now > DURATION:
            break

    env.run()


if __name__ == "__main__":
    main()
