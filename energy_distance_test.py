# -*- coding: utf-8 -*-
"""energy_distance_test.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qCHfqEVxpDLyoFeCI1rl55nzcGUDO1md
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

# Load the two datasets (MCI and NC) from CSV files
file_mci = "/content/drive/MyDrive/radiomic_features_bratshgg_dec22.csv"  # Replace with your actual file path
file_nc = "/content/drive/MyDrive/radiomic_features_bratslgg_dec22.csv"    # Replace with your actual file path
data_mci = pd.read_csv(file_mci)
data_nc = pd.read_csv(file_nc)

if data_mci.columns[0].lower() in ["id", "subject_id"]:
    data_mci = data_mci.drop(columns=data_mci.columns[0])
    data_nc = data_nc.drop(columns=data_nc.columns[0])

def extract_number(array_string):
    if isinstance(array_string, str) and 'array' in array_string:
        return float(array_string.split('(')[1].split(')')[0])
    else:
        return array_string

# Apply the function to each column
for column in data_mci .columns:
    data_mci [column] = data_mci [column].apply(extract_number)

for column in data_nc .columns:
    data_nc [column] = data_nc [column].apply(extract_number)


# Drop the identifier column if present
if data_mci.columns[0].lower() in ["id", "subject_id"]:
    data_mci = data_mci.drop(columns=data_mci.columns[0])
    data_nc = data_nc.drop(columns=data_nc.columns[0])

# Define the Energy Distance function
def energy_distance_test(group1, group2):
    # Pairwise distances within and between groups
    d_within_1 = cdist(group1[:, None], group1[:, None], metric='euclidean')
    d_within_2 = cdist(group2[:, None], group2[:, None], metric='euclidean')
    d_between = cdist(group1[:, None], group2[:, None], metric='euclidean')

    # Calculate energy distance components
    within_1_mean = np.mean(d_within_1)
    within_2_mean = np.mean(d_within_2)
    between_mean = np.mean(d_between)

    # Energy distance statistic
    energy_stat = 2 * between_mean - within_1_mean - within_2_mean

    return energy_stat

# Perform Energy Distance test for each feature
results = []
for feature in data_mci.columns:
    # Extract feature values for MCI and NC groups
    mci_values = data_mci[feature].values
    nc_values = data_nc[feature].values

    # Calculate energy distance
    energy_stat = energy_distance_test(mci_values, nc_values)

    # Append results
    results.append((feature, energy_stat))

# Convert results to a DataFrame for easy analysis
results_df = pd.DataFrame(results, columns=["Feature", "Energy Statistic"])

# Sort features by energy statistic (higher indicates more dissimilarity)
results_df = results_df.sort_values(by="Energy Statistic", ascending=False)

# Save results to a CSV file
results_df.to_csv("energy_distance_results.csv", index=False)

# Display the top features
print(f"Top Features by Energy Distance:\n{results_df.head()}")

# Type 1 and Type 2 Error Analysis
from sklearn.utils import resample
def calculate_errors_and_power(data_mci, data_nc, num_permutations=1000, alpha=0.05):
    type_1_errors = []
    type_2_errors = []
    power_values = []

    for feature in data_mci.columns:
        # Extract feature values
        mci_values = data_mci[feature].values
        nc_values = data_nc[feature].values

        # Observed energy statistic
        observed_stat = energy_distance_test(mci_values, nc_values)

        # Permutation testing
        all_values = np.concatenate([mci_values, nc_values])
        permuted_stats = []

        for _ in range(num_permutations):
            permuted = resample(all_values, replace=False)
            perm_mci = permuted[:len(mci_values)]
            perm_nc = permuted[len(mci_values):]
            perm_stat = energy_distance_test(perm_mci, perm_nc)
            permuted_stats.append(perm_stat)

        # Calculate p-value
        p_value = np.mean(np.array(permuted_stats) >= observed_stat)

        # Type 1 error (false positive)
        type_1 = p_value < alpha
        type_1_errors.append(type_1)

        # Type 2 error (false negative)
        type_2 = not type_1
        type_2_errors.append(type_2)

        # Power (1 - Type 2 error)
        power = 1 - type_2
        power_values.append(power)

    return type_1_errors, type_2_errors, power_values

type_1_errors, type_2_errors, power_values = calculate_errors_and_power(data_mci, data_nc)

# Print summary
print("Type 1 Errors:", sum(type_1_errors))
print("Type 2 Errors:", sum(type_2_errors))
print("Power Values:", np.mean(power_values))

def calculate_errors_and_power(data_mci, data_nc, num_permutations=1000, alpha=0.05):
    total_features = len(data_mci.columns)
    type_1_error_count = 0
    type_2_error_count = 0

    for feature in data_mci.columns:
        # Extract feature values
        mci_values = data_mci[feature].values
        nc_values = data_nc[feature].values

        # Observed energy statistic
        observed_stat = energy_distance_test(mci_values, nc_values)

        # Permutation testing
        all_values = np.concatenate([mci_values, nc_values])
        permuted_stats = []

        for _ in range(num_permutations):
            permuted = resample(all_values, replace=False)
            perm_mci = permuted[:len(mci_values)]
            perm_nc = permuted[len(mci_values):]
            perm_stat = energy_distance_test(perm_mci, perm_nc)
            permuted_stats.append(perm_stat)

        # Calculate p-value
        p_value = np.mean(np.array(permuted_stats) >= observed_stat)

        # Type 1 error: Reject null when it is true
        if p_value < alpha:
            type_1_error_count += 1

        # Type 2 error: Fail to reject null when it is false
        if p_value >= alpha:
            type_2_error_count += 1

    # Calculate error rates and power
    type_1_error_rate = type_1_error_count / total_features
    type_2_error_rate = type_2_error_count / total_features
    power = 1 - type_2_error_rate

    return type_1_error_rate, type_2_error_rate, power

# Calculate Type 1 error, Type 2 error, and power
type_1_error_rate, type_2_error_rate, power = calculate_errors_and_power(data_mci, data_nc)

# Print summary
print(f"Type 1 Error Rate: {type_1_error_rate:.3f}")
print(f"Type 2 Error Rate: {type_2_error_rate:.3f}")
print(f"Power: {power:.3f}")