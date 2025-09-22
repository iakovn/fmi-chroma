# ...existing code...
from dataclasses import dataclass
from typing import Any


class ClassInformationAPIError(ValueError):
    """Raised when the result from OMC is not as expected."""

    def __init__(self, t: tuple[Any, ...]):
        super().__init__(
            f"Expected 22 elements for ClassInformation, got {len(t)}"
        )
        self.t = t


@dataclass
class ClassInformation:
    restriction: str
    comment: str
    partialPrefix: bool
    finalPrefix: bool
    encapsulatedPrefix: bool
    fileName: str
    fileReadOnly: bool
    lineNumberStart: int
    columnNumberStart: int
    lineNumberEnd: int
    columnNumberEnd: int
    dimensions: list[str]
    isProtectedClass: bool
    isDocumentationClass: bool
    version: str
    preferredView: str
    state: bool
    access: str
    versionDate: str
    versionBuild: str
    dateModified: str
    revisionId: str

    @classmethod
    def from_tuple(cls, t: tuple[Any, ...]) -> "ClassInformation":
        # Convert the tuple to a ClassInformation instance
        # with appropriate type conversions.
        if len(t) != 22:
            raise ClassInformationAPIError(t)

        # Note: the order and types must match the output of getClassInformation
        # map tuple elements to fields in the documented order
        return cls(
            restriction=str(t[0]),
            comment=str(t[1]),
            partialPrefix=bool(t[2]),
            finalPrefix=bool(t[3]),
            encapsulatedPrefix=bool(t[4]),
            fileName=str(t[5]),
            fileReadOnly=bool(t[6]),
            lineNumberStart=int(t[7]),
            columnNumberStart=int(t[8]),
            lineNumberEnd=int(t[9]),
            columnNumberEnd=int(t[10]),
            dimensions=list(map(str, t[11])) if t[11] is not None else [],
            isProtectedClass=bool(t[12]),
            isDocumentationClass=bool(t[13]),
            version=str(t[14]),
            preferredView=str(t[15]),
            state=bool(t[16]),
            access=str(t[17]),
            versionDate=str(t[18]),
            versionBuild=str(t[19]),
            dateModified=str(t[20]),
            revisionId=str(t[21]),
        )
