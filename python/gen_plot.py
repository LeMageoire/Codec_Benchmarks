import numpy as np
import matplotlib.pyplot as plt

# Parameters
original_file_size = 1000000  # in bytes, e.g., 1MB file
error_rates = [0.01]  # 1% error rate
redundancies = [6, 8, 10, 12]  # Different levels of redundancy (RS bytes)

# Simulated function to calculate added nucleotide rate
def calculate_added_nucleotide_rate(file_size, redundancy, error_rate):
    # Simulate how redundancy affects file size
    encoded_file_size = file_size * (1 + redundancy / 100.0)  # simplified assumption
    return 100 * (encoded_file_size - file_size) / file_size

# Simulated function to calculate decoding success rate
def calculate_success_rate(redundancy, error_rate):
    # Assuming success rate increases with more redundancy and less error rate
    return np.clip(100 - (error_rate * 100) + redundancy * 2, 0, 100)

# Collecting data
x_data = {}  # Relative added nucleotide rate
y_data = {}  # Decoding success rate

for redundancy in redundancies:
    x_data[redundancy] = []
    y_data[redundancy] = []
    for error_rate in error_rates:
        added_rate = calculate_added_nucleotide_rate(original_file_size, redundancy, error_rate)
        success_rate = calculate_success_rate(redundancy, error_rate)
        x_data[redundancy].append(added_rate)
        y_data[redundancy].append(success_rate)

# Plotting
plt.figure(figsize=(10, 6))
for redundancy in redundancies:
    plt.plot(x_data[redundancy], y_data[redundancy], marker='o', label=f'RS bytes {redundancy}')
plt.title('Decoding success rate analysis\nError rate 1%')
plt.xlabel('Relative added nucleotide rate (%)')
plt.ylabel('Decoding success rate (%)')
plt.legend()
plt.grid(True)
plt.show()


import numpy as np
import matplotlib.pyplot as plt
import json

# JSON data
json_data = """
{
  "benchmarks": [
    {
      "name": "DNA-Aeon",
      "description": "codec of DNA-Aeon",
      "args": {
        "error_rate_min": 0.01,
        "error_rate_max": 0.02,
        "error_rate_step": 5,
        "package_redundancy_min": 0,
        "package_redundancy_max": 0.5,
        "package_redundancy_step": 5,
        "num_iters": 100
      }
    }
  ]
}
"""

# Parsing JSON
data = json.loads(json_data)
benchmark = data['benchmarks'][0]['args']

# Generate combinations of error rates and package redundancies
error_rates = np.linspace(benchmark['error_rate_min'], benchmark['error_rate_max'], benchmark['error_rate_step'])
package_redundancies = np.linspace(benchmark['package_redundancy_min'], benchmark['package_redundancy_max'], benchmark['package_redundancy_step'])

# Placeholder function to simulate decoding success rate
def simulate_success_rate(error_rate, package_redundancy):
    # Simulated success rate based on package redundancy and error rate
    return 100 - (error_rate * 100) + (package_redundancy * 100)

# Data for plotting
plot_data = {error_rate: [] for error_rate in error_rates}

for error_rate in error_rates:
    for redundancy in package_redundancies:
        success_rate = simulate_success_rate(error_rate, redundancy)
        relative_bitrate_added = 100 * redundancy  # Convert package redundancy to relative added bitrate
        plot_data[error_rate].append((relative_bitrate_added, success_rate))

# Create a plot for each error rate
for error_rate in error_rates:
    plt.figure()
    rates, successes = zip(*plot_data[error_rate])
    plt.plot(rates, successes, marker='o', linestyle='-', label=f'Error Rate: {error_rate*100:.2f}%')
    plt.title(f'Success Rate vs. Relative Bitrate Added at Error Rate {error_rate*100:.2f}%')
    plt.xlabel('Relative Bitrate)
    plt.ylabel('Success Rate (%)')