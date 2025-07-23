# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     notebook_metadata_filter: all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.12.11
# ---

# %% [markdown]
# # Demo Notebook
# This is a demo for Jupytext synchronization.

# %% [markdown]
# ## Example: Compile Modelica Model to FMU, Simulate, and Plot Results
#
# This example demonstrates how to:
# 1. Export `Modelica.Fluid.Examples.HeatingSystem` as a Co-Simulation FMU using OMPython.
# 2. Simulate the FMU using fmpy.
# 3. Plot sensor outputs (e.g., rotations speed) as a function of time.

# %%
import os

import matplotlib.pyplot as plt
from fmpy import simulate_fmu
from OMPython import OMCSessionZMQ

from fmi_chroma.ompython import (
    FMUExportError,
    ModelicaLoadError,
    ensure_modelica_library,
    execute_omc_command,
)

# %%
omc = OMCSessionZMQ()
execute_omc_command(
    omc, 'cd("/workspaces/fmi-chroma/.generated")', "Failed to change directory"
)

# %%
# Settings
model_name = "Modelica.Fluid.Examples.HeatingSystem"
model_name = "Modelica.Fluid.Examples.PumpingSystem"
model_name = "Modelica.Blocks.Examples.PID_Controller"
fmu_filename = (
    f"/workspaces/fmi-chroma/.generated/{model_name.split('.')[-1]}.fmu"
)

# Step 1: Export the Modelica model as a Co-Simulation FMU
if not os.path.exists(fmu_filename):
    print(f"Exporting {model_name} to {fmu_filename} ...")

    # Ensure Modelica Standard Library 4.0.0 is available
    if not ensure_modelica_library(omc, version="4.0.0"):
        raise ModelicaLoadError()

    # Build the FMU
    try:
        fmu_filename = execute_omc_command(
            omc,
            f'buildModelFMU({model_name}, version="2.0", fmuType="cs")',
            f"Failed to export {model_name} as an FMU",
        )
        print(f"FMU exported: {fmu_filename}")
    except RuntimeError as e:
        raise FMUExportError(str(e)) from e
else:
    print(f"FMU already exists: {fmu_filename}")

# %%
# Step 2: Collect and print diagram information
# Load the model for inspection
execute_omc_command(
    omc, f"loadModel({model_name})", f"Failed to load {model_name}"
)

# Get all components in a single call
print(f"Fetching components for {model_name}...")
components = (
    execute_omc_command(
        omc,
        f"getComponents({model_name})",
        f"Failed to get components for {model_name}",
    )
    or []
)
print(f"Found {len(components)} components.")

# Get all connections in a single call
print(f"Fetching connections for {model_name}...")
connections = (
    execute_omc_command(
        omc,
        f"getConnectionList({model_name})",
        f"Failed to get connections for {model_name}",
    )
    or []
)
print(f"Found {len(connections)} connections.")

print("\n--- Components ---")
for comp in components:
    # Record: {className, instanceName, origin, extent, rotation}
    print(f"  - Class: {comp[1]}, Name: {comp[2]}")


print("\n--- Connections ---")
for conn in connections:
    # Record: {from, to, color, lineStyle, etc.}
    print(f"  - From: {conn[0]} To: {conn[1]}")


# %%
# Step 3: Simulate the FMU using fmpy
print("Simulating the FMU ...")
result = simulate_fmu(fmu_filename, start_time=0, stop_time=4)

# Step 4: Plot results
# List available variables
print("Available variables:", result.dtype.names)

# Example: Plot rotation speed as a function of time
plt.figure(figsize=(10, 6))
plt.plot(result["time"], result["inertia2.w"], label="inertia2.w")

plt.xlabel("Time [s]")
plt.ylabel("Temperature [K]")
plt.title("Sensor Temperatures vs Time")
plt.legend()
plt.grid(True)
plt.show()
