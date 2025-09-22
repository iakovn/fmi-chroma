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
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from fmpy import (
    extract as extract_fmu,
)
from fmpy import (
    instantiate_fmu,
    read_model_description,
    simulate_fmu,
)
from OMPython import OMCSessionZMQ

import fmi_chroma
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

# %%
# Step 1: Load MSL and analyze the mode
# Ensure Modelica Standard Library 4.0.0 is available
if not ensure_modelica_library(omc, version="4.0.0"):
    raise ModelicaLoadError()

class_information = execute_omc_command(
    omc, f"getClassInformation({model_name})"
)

print(f"Class information for {model_name}:")
print(class_information)

path_to_MSL = Path(execute_omc_command(omc, "getSourceFile(Modelica)")).parent


# %%
# See how things work with a small Modelica code as a string
package_name = "SmallTest"
model_code = f"""
package {package_name}
model PID2
  Modelica.Blocks.Continuous.PID pid1(k=1, Ti=1, Td=0.1);
  Modelica.Blocks.Continuous.PID pid2(k=2, Ti=2, Td=0.1);
  parameter Real x = 0.5;
  annotation(some="thing", other=123, __TestSpecification(p1=true, p2=2, p3="hello", p4=3.0));
end PID2;
model TestPID
    extends Modelica.Blocks.Examples.PID_Controller;
end TestPID;
end {package_name};
"""

generated_path = Path(f"/tmp/{package_name}.mo")  # noqa: S108
with open(generated_path, "w") as f:
    f.write(model_code)

test_lib_path = (
    Path(fmi_chroma.__file__).parent / "MyTestLibrary" / "package.mo"
)
if not test_lib_path.exists():
    test_lib_path = (
        Path(fmi_chroma.__file__).parent.parent.parent
        / "tests"
        / "MyTestLibrary"
        / "package.mo"
    )
libpath = (
    omc.sendExpression("getModelicaPath()")
    + os.pathsep
    + str(test_lib_path.parent.parent)
    + os.pathsep
    + str(generated_path.parent)
)
execute_omc_command(
    omc,
    f'setModelicaPath("{libpath}")',
    "Failed to set Modelica path",
)

for load_library_path in [test_lib_path, generated_path]:
    if not execute_omc_command(omc, f'loadFile("{load_library_path!s}")'):
        print(f"Failed to load library from {load_library_path!s}")
        err = omc.sendExpression("getErrorString()")
        print(err)
        continue
    package = Path(load_library_path).stem
    if package == "package":
        package = Path(load_library_path).parent.name
    print(f"\nClass information for {package}:")
    class_info = execute_omc_command(omc, f"getClassInformation({package})")
    print(class_info)

    models_in_package = execute_omc_command(
        omc, f"getClassNames({package}, true, true)"
    )

    print(f"Models in {package}: {models_in_package}")

    for class_name in models_in_package:
        print(f"\nLoading {class_name}:")
        if not execute_omc_command(omc, f"loadModel({class_name})"):
            err = omc.sendExpression("getErrorString()")
            print(err)
            continue
        if class_name == package:
            continue  # Skip the package itself
        print(f"\nClass information for {class_name}:")
        class_info = execute_omc_command(
            omc, f"getClassInformation({class_name})"
        )
        print(class_info)
        print(
            execute_omc_command(omc, f"getClassNames({class_name}, true, true)")
        )
        # For more detailed dependency list:
        used_classes = execute_omc_command(
            omc, f"getUsedClassNames({class_name})"
        )
        print(f"Used classes in {class_name}:")
        print(", ".join(used_classes))
        files = {
            execute_omc_command(omc, f"getSourceFile({class_name})")
            for class_name in used_classes
        }
        print("\nSource files:")
        print(", ".join(files))

        try:
            modifier_spec_names = execute_omc_command(
                omc,
                f'getAnnotationNamedModifiers({class_name},"__TestSpecification")',
            )
        except RuntimeError:  # If annotation does not exist
            print(f"No __TestSpecification annotation in {class_name}")
            continue
        test_spec_mods = {
            m: execute_omc_command(
                omc,
                f'getAnnotationModifierValue({class_name}, "__TestSpecification", "{m}")',
            )
            for m in modifier_spec_names
        }
        print("Modifiers in test spec:")
        print("\n".join(f"{m}={v}" for m, v in test_spec_mods.items()))
# %%
# Step 1: Export the Modelica model as a Co-Simulation FMU
if not os.path.exists(fmu_filename):
    print(f"Exporting {model_name} to {fmu_filename} ...")

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

# %%
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
# %%
print("\n--- Components ---")
for i, comp in enumerate(components):
    # comp is a tuple (type,name,description, ...)
    comp_type, comp_name = comp[0], comp[1]

    # annotations are expressions that will need further processing
    comp_annotation = execute_omc_command(
        omc,
        f"getNthComponentAnnotation({model_name}, {i + 1})",
        f"Failed to get component annotation{i}",
        parsed=False,
    )
    icon_annotation = execute_omc_command(
        omc,
        f"getIconAnnotation({comp_type})",
        f"Failed to get component icon annotation{i}",
        parsed=False,
    )

    print(
        f"  - Class: {comp_type}, Name: {comp_name}, Annotation: {comp_annotation}, Icon: {icon_annotation}"
    )


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
plt.ylabel("Rotation speed [rad/s]")
plt.title("Rotation speed vs Time")
plt.legend()
plt.grid(True)
plt.show()

# %%

# Create a temporary directory
tmpdir = tempfile.TemporaryDirectory()
print("Created temporary directory:", tmpdir.name)

# extract fmu
dirname = extract_fmu(fmu_filename, tmpdir.name)

# %%

md = read_model_description(dirname)
mv = pd.DataFrame(vars(v) for v in md.modelVariables).set_index("name")

print(f"The model contains {len(mv)} model variables")

# %%
fmu = instantiate_fmu(
    dirname,
    md,
)

# Perform operations within this directory
# %%
fmu.instantiate()

# %%
mv.at["inertia1.J", "valueReference"]

# %%
fmu.setReal([mv.at["inertia1.J", "valueReference"]], [2.0])
# %%
# Manually clean up the directory
tmpdir.cleanup()
