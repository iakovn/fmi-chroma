"""Pytest plugin stubs for Modelica support.

This module currently provides a placeholder for pytest_collect_file
to be implemented later.
"""

import os
import warnings
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from fmi_chroma.introspection.types import ClassInformation

if TYPE_CHECKING:
    from OMPython import OMCSessionZMQ


@lru_cache
def get_omc_session(_=0) -> "OMCSessionZMQ":
    from OMPython import OMCSessionZMQ

    return OMCSessionZMQ()


def pytest_collect_file(parent: Path, file_path: Path) -> Any | None:
    """Placeholder hook for pytest collection.

    Return a pytest Collector instance when `path` should be collected,
    otherwise return None. Implementation to be added later.
    """
    if file_path.suffix == ".mo":
        if file_path.name.lower() == "package.mo" or (
            "TEST" in file_path.name.upper()
        ):
            return ModelicaFile.from_parent(parent, path=file_path)
        else:
            warnings.warn(
                f"Skipping {file_path}: does not match test naming conventions",
                pytest.PytestCollectionWarning,
                stacklevel=1,
            )


def ensure_modelica_path(omc: "OMCSessionZMQ", path: Path) -> None:
    """Ensure the given path is in the Modelica path."""
    library_path = path.parent
    # Ascend to the directory containing package.mo
    while (library_path.parent / "package.mo").exists():
        library_path = library_path.parent
    str_path = str(library_path.parent)
    current_paths = omc.sendExpression("getModelicaPath()")
    if str_path not in current_paths:
        warnings.warn(
            f"Adding missing Modelica Path {str_path}",
            pytest.PytestCollectionWarning,
            stacklevel=1,
        )

        new_path = current_paths + os.pathsep + str_path
        omc.sendExpression(f'setModelicaPath("{new_path}")')


@lru_cache
def load_modelica_library(omc: "OMCSessionZMQ", library_name: str) -> None:
    if not omc.sendExpression(f"loadModel({library_name})"):
        error_string = omc.sendExpression("getErrorString()")
        warnings.warn(
            f"OMC Error loading model {library_name}: {error_string}",
            pytest.PytestCollectionWarning,
            stacklevel=1,
        )


class ModelicaFile(pytest.File):
    def collect(self):  # noqa: C901
        omc = get_omc_session()
        file_name = self.path
        ensure_modelica_path(omc, Path(file_name))
        class_names = omc.sendExpression(f'parseFile("{file_name!s}")')
        error_string = omc.sendExpression("getErrorString()")
        if error_string:
            warnings.warn(
                f"OMC Error parsing {file_name}: {error_string}",
                pytest.PytestCollectionWarning,
                stacklevel=1,
            )
        if class_names:
            library_name = class_names[0].split(".")[0]
            load_modelica_library(omc, library_name)

        if class_names and file_name.name.lower() == "package.mo":
            package_name = class_names[0]
            class_names = omc.sendExpression(
                f"getClassNames({package_name},true)"
            )
            error_string = omc.sendExpression("getErrorString()")
            if error_string:
                warnings.warn(
                    f"OMC Error processing {file_name}: {package_name}: {error_string}",
                    pytest.PytestCollectionWarning,
                    stacklevel=1,
                )

        for class_name in class_names:
            if not (class_name and "TEST" in class_name.upper()):
                warnings.warn(
                    f"Skipping {file_name}: {class_name}",
                    pytest.PytestCollectionWarning,
                    stacklevel=1,
                )
                continue
            class_information = omc.sendExpression(
                f"getClassInformation({class_name})"
            )
            error_string = omc.sendExpression("getErrorString()")
            if error_string:
                warnings.warn(
                    f"OMC Error processing {file_name}: {class_name}: {error_string}",
                    pytest.PytestCollectionWarning,
                    stacklevel=1,
                )
            if not class_information:
                continue
            try:
                ci = ClassInformation.from_tuple(class_information)
            except Exception as e:
                warnings.warn(
                    f"Failed to parse ClassInformation {class_information} in {file_name}: {class_name}: {e}",
                    pytest.PytestCollectionWarning,
                    stacklevel=1,
                )
                continue
            if ci.fileName != str(file_name):
                # Skip classes not defined in this file (relevant for packages)
                continue
            if ci.restriction != "model":
                continue
            lineno = ci.lineNumberStart
            item = ModelicaItem.from_parent(
                self, name=class_name, spec=class_name, lineno=lineno
            )
            item.lineno = lineno
            yield item


class ModelicaItem(pytest.Item):
    def __init__(self, *, spec, lineno: int, **kwargs):
        super().__init__(**kwargs)
        self.spec = spec
        self.lineno = lineno or 0

    @property
    def location(self):
        # (relpath, lineno, test name)
        return str(self.fspath), self.lineno, self.name

    def runtest(self):
        pass

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        pass

    def reportinfo(self):
        return self.path, 0, f"usecase: {self.path}:{self.spec}"
