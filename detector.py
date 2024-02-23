import simpy
import random
import numpy as np
import sklearn
from sklearn.neural_network import MLPClassifier

particle = [gamma, neutron]

# simulate the interaction of a particle with an organic scintillator and emission of photons
def scintillator(particle_type, energy):

    # Define interaction probability based on particle type and energy
    if particle_type == "gamma":
        interaction_prob = 0.9 * np.exp(-energy / 0.5)
    elif particle_type == "neutron":
        interaction_prob = 0.5 * np.exp(-energy / 1.0)
    else:
        raise ValueError("Invalid particle type")
    
    # Check if interaction occurs
    if random.random() < interaction_prob:
        # Define decay constant based on particle type 
        if particle_type == "gamma":
            decay_constant = 1e7  # Hz
        elif particle_type == "neutron":
            decay_constant = 5e6  # Hz
        else:
            raise ValueError("Invalid particle type")

        # Define emission spectrum based on particle type 
        if particle_type == "gamma":
            wavelengths = np.random.choice([400, 450, 500], size=10, p=[0.3, 0.5, 0.2])  # nm
            intensities = np.random.uniform(0.5, 1.0, size=10)
        elif particle_type == "neutron":
            wavelengths = np.random.choice([600, 650, 700], size=5, p=[0.2, 0.6, 0.2])  # nm
            intensities = np.random.uniform(0.1, 0.3, size=5)
        else:
            raise ValueError("Invalid particle type")

        # Generate photons with random arrival times based on exponential decay
        photons = []
        for wavelength, intensity in zip(wavelengths, intensities):
            arrival_time = -np.log(random.random()) / decay_constant
            photons.append({"wavelength": wavelength, "intensity": intensity, "arrival_time": arrival_time})
    
        #return list of emitted photons and properties as a dictionary
        return photons

    else:
        return []  # No interaction, return empty list


# simulate the response of a photomultiplier tube to a list of photons
def photomultiplier(arrival_time, wavelength, energy):
    # Define PMT sensitivity curve 
    sensitivity = np.interp(np.linspace(300, 800, 1000), [0.1, 0.5, 1.0, 0.8, 0.2], np.linspace(300, 800, 1000))

    # Create empty signal array
    signal = np.zeros(1000)  # Adjust time resolution based on your needs

    # Iterate over each photon
    for photon in photons:
        wavelength = photon["wavelength"]
        intensity = photon["intensity"]
        arrival_time = photon["arrival_time"]

    # Convert arrival time to index for signal array
    index = int(arrival_time * signal.size)

    # Apply PMT sensitivity and intensity
    response = intensity * sensitivity[wavelength]

    # Add response to signal, considering time resolution
    signal[max(0, index - 1):min(index + 2, signal.size)] += response

    # Add noise 
    signal += np.random.normal(0, 0.01, signal.size)

    # the simulated voltage over time (as a numpy array)
    return signal


def preamp(signal):
    # Apply gain 
    gain = 100

    preamp_signal = signal * gain

    # Apply some filtering 
    preamp_signal = np.convolve(preamp_signal, np.ones(5) / 5, mode='same')

    # Adding noise 
    preamp_signal += np.random.normal(0, 0.02, signal.size)

    # pre-amplified and filtered signal
    return preamp_signal


# use previous three functions to perform PSD
def main():
    # Simulation parameters
    particle_rate = 1000 # Hz
    simulation_time = 10 # seconds
    energy_range = (0.5, 2.0) # MeV

    # Initialize SimPy environment
    env = simpy.Environment()

    # Define particle arrival process
    def particle_arrivals(env):
        while True:
            particle_type = random.choice(["gamma", "neutron"])
            energy = random.uniform(*energy_range)
            env.process(scintillation_process(env, particle_type, energy))
            yield env.timeout(1 / particle_rate)
    
    env.process(particle_arrivals(env))

    def scintillation_process(env, particle_type, energy):
        photons = scintillator(particle_type, energy)
        if photons:
            signal = photomultiplier(photons)

        # Optional preamp:
        preprocessed_signal = preamp(signal)

        # Feature extraction from preprocessed signal
        features = extract_features(signal)  # Implement your feature extraction logic here

        # PSD using trained model:
        predicted_type = psd_model.predict([features])[0]  # Replace with your PSD model

        # Track data for analysis:
        data.append({"true_type": particle_type, "predicted_type": predicted_type, "features": features})
    
    # Feature extraction function:
    def extract_features(signal):
        rise_time = ...  
        decay_time = ...
        area = ...
        ...
        return [rise_time, decay_time, area, ...]

    # PSD model 
    # Will load PSD model here
    psd_model = MLPClassifier(...)

    # Data collection list
    data = []

    # Start simulation and collect data
    env.run(until=simulation_time)

    # Analyze collected data:
    analyze_data(data)  # still have to define analyze_data 


    if __name__ == "__main__":
        main()
