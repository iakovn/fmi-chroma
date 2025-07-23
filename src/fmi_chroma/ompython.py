"""A module for interacting with OpenModelica via OMPython."""

from typing import Any

from OMPython import OMCSessionZMQ


def execute_omc_command(
    omc: OMCSessionZMQ,
    command: str,
    error_message: str = "",
    parsed: bool = True,
) -> Any:
    """
    Execute an OMC command and handle errors.

    Args:
        omc: OMCSessionZMQ instance
        command: Command to execute
        error_message: Custom error message to display if command fails

    Returns:
        The result of the command or raises RuntimeError if it fails
    """
    result = omc.sendExpression(command, parsed=parsed)
    if result is None:
        error = (
            omc.sendExpression("getErrorString()", parsed=False)
            or "No error details available"
        )
        full_error = (
            f"{error_message}\nError executing command: {command}\n{error}"
        )
        raise RuntimeError(full_error)
    return result


class ModelicaLoadError(Exception):
    """Raised when loading the Modelica library fails."""

    def __init__(
        self, message="Failed to ensure Modelica Standard Library is available"
    ):
        self.message = message
        super().__init__(self.message)


class FMUExportError(Exception):
    """Raised when FMU export fails."""

    pass


def ensure_modelica_library(omc, version="4.0.0"):
    """
    Ensure Modelica Standard Library is available, install if necessary.

    Args:
        omc: OMCSessionZMQ instance
        version: Modelica Standard Library version to install (default: "4.0.0")

    Returns:
        bool: True if library is available, raises exception on error
    """
    print(f"Checking for Modelica Standard Library version {version}...")

    # First, try to load the Modelica library
    try:
        result = execute_omc_command(
            omc,
            f'loadModel(Modelica,{{"{version}"}})',
            f"Failed to load Modelica Standard Library {version}",
        )
    except RuntimeError as e:
        print(
            f"Modelica Standard Library {version} not found. Attempting to install..."
        )
        print(f"Note: {str(e).splitlines()[0]}")
    else:
        print(f"Modelica Standard Library {version} loaded ({result}).")
        return True

    try:
        # Try to install the specific version using installPackage
        print(f"Installing Modelica Standard Library {version}...")
        execute_omc_command(
            omc,
            f'installPackage(Modelica, "{version}")',
            f"Failed to install Modelica Standard Library {version}",
        )

        print(f"Successfully installed Modelica Standard Library {version}")

        # Verify the installation by loading it
        try:
            execute_omc_command(
                omc,
                f'loadModel(Modelica,{{"{version}"}})',
                "Installation reported success but library failed to load",
            )
        except RuntimeError as load_error:
            print(
                f"Failed to load installed library: {str(load_error).splitlines()[0]}"
            )
            return False
        else:
            print("Modelica library loaded successfully after installation.")
            return True

    except RuntimeError as e:
        print(
            f"Failed to install Modelica Standard Library: {str(e).splitlines()[0]}"
        )
        print("Please install it manually or check your installation.")
        return False
