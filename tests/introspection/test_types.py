from fmi_chroma.introspection.types import ClassInformation


# Simple pytest-style test: verifies parsing of the provided example tuple
def test_class_information_from_example_tuple() -> None:
    example = (
        "package",
        "",
        False,
        False,
        False,
        "/workspaces/fmi-chroma/src/fmi_chroma/MyTestLibrary/package.mo",
        False,
        2,
        1,
        15,
        18,
        (),
        False,
        False,
        "",
        "",
        False,
        "",
        "",
        "",
        "",
        "",
    )
    ci = ClassInformation.from_tuple(example)
    assert ci.restriction == "package"
    assert ci.comment == ""
    assert ci.partialPrefix is False
    assert ci.finalPrefix is False
    assert ci.encapsulatedPrefix is False
    assert ci.fileName.endswith("MyTestLibrary/package.mo")
    assert ci.fileReadOnly is False
    assert ci.lineNumberStart == 2
    assert ci.columnNumberStart == 1
    assert ci.lineNumberEnd == 15
    assert ci.columnNumberEnd == 18
    assert ci.dimensions == []
    assert ci.isProtectedClass is False
    assert ci.isDocumentationClass is False
    assert ci.version == ""
    assert ci.preferredView == ""
    assert ci.state is False
    assert ci.access == ""
    assert ci.versionDate == ""
    assert ci.versionBuild == ""
    assert ci.dateModified == ""
    assert ci.revisionId == ""
