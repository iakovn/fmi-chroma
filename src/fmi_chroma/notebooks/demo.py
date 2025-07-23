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
#     name: python
#     version: '3.11'
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
# 3. Plot sensor outputs (e.g., temperature) as a function of time.

# %%
import os

import matplotlib.pyplot as plt
from fmpy import simulate_fmu
from OMPython import OMCSessionZMQ


class ModelicaLoadError(Exception):
    """Raised when loading the Modelica library fails."""

    pass


class FMUExportError(Exception):
    """Raised when FMU export fails."""

    pass


# Settings
model_name = "Modelica.Fluid.Examples.HeatingSystem"
fmu_filename = "HeatingSystem.fmu"

# Step 1: Export the Modelica model as a Co-Simulation FMU
omc = OMCSessionZMQ()
if not os.path.exists(fmu_filename):
    print(f"Exporting {model_name} to {fmu_filename} ...")
    # Make sure Modelica Standard Library is available in your OMC
    res = omc.sendExpression("loadModel(Modelica)")
    if not res:
        # Full context: Failed to load Modelica library for FMU export
        raise ModelicaLoadError
    res = omc.sendExpression(
        f'buildModelFMU({model_name}, version="2.0", fmuType="cs", fileNamePrefix="HeatingSystem")'
    )
    if not res:
        # Full context: FMU export failed for the Modelica model
        raise FMUExportError
    print(f"FMU exported: {fmu_filename}")
else:
    print(f"FMU already exists: {fmu_filename}")

# Step 2: Simulate the FMU using fmpy
print("Simulating the FMU ...")
result = simulate_fmu(fmu_filename, start_time=0, stop_time=5000)

# Step 3: Plot results
# List available variables
print("Available variables:", result.dtype.names)

# Example: Plot temperatures of two sensors as a function of time
plt.figure(figsize=(10, 6))
plt.plot(result["time"], result["heatingSystem.TSensor1.T"], label="TSensor1.T")
plt.plot(result["time"], result["heatingSystem.TSensor2.T"], label="TSensor2.T")
plt.xlabel("Time [s]")
plt.ylabel("Temperature [K]")
plt.title("Sensor Temperatures vs Time")
plt.legend()
plt.grid(True)
plt.show()

# Note: Variable names may differ depending on the FMU structure. Use the print above to inspect them.
