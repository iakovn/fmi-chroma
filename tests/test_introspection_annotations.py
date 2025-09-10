"""Unit tests for the annotations module."""

from fmi_chroma.introspection.annotations.parser import (
    parse_icon_annotation,
    parse_placement_annotation,
)
from fmi_chroma.introspection.annotations.types import (
    Arrow,
    BorderPattern,
    CoordinateSystem,
    FillPattern,
    Icon,
    Line,
    LinePattern,
    Placement,
    Rectangle,
    Smooth,
    Text,
    TextAlignment,
)


def test_parse_icon_annotation():
    """Test parsing a full getIconAnnotation string."""
    annotation_string = (
        "{-100.0,-100.0,100.0,100.0,true,0.1,,"
        "{Rectangle(true,{0.0,0.0},0.0,{64,64,64},{192,192,192},"
        "LinePattern.Solid,FillPattern.HorizontalCylinder,0.25,"
        "BorderPattern.None,{{-100.0,-10.0},{-50.0,10.0}},0.0),"
        "Rectangle(true,{0.0,0.0},0.0,{64,64,64},{192,192,192},"
        "LinePattern.Solid,FillPattern.HorizontalCylinder,0.25,"
        "BorderPattern.None,{{50.0,-10.0},{100.0,10.0}},0.0),"
        "Line(true,{0.0,0.0},0.0,{{-80.0,-25.0},{-60.0,-25.0}},{0,0,0},"
        "LinePattern.Solid,0.25,{Arrow.None,Arrow.None},3.0,Smooth.None),"
        'Text(true,{0.0,0.0},0.0,{{-150.0,60.0},{150.0,100.0}},"%name",0.0,"",{},{0,0,0},TextAlignment.Center,0)}}'
    )

    expected = Icon(
        coordinate_system=CoordinateSystem(
            extent=((-100.0, -100.0), (100.0, 100.0)),
            preserve_aspect_ratio=True,
            initial_scale=0.1,
            grid=(1.0, 1.0),  # Default value
        ),
        graphics=[
            Rectangle(
                visible=True,
                origin=(0.0, 0.0),
                rotation=0.0,
                line_color=(64, 64, 64),
                fill_color=(192, 192, 192),
                pattern=LinePattern.SOLID,
                fill_pattern=FillPattern.HORIZONTAL_CYLINDER,
                line_thickness=0.25,
                border_pattern=BorderPattern.NONE,
                extent=((-100.0, -10.0), (-50.0, 10.0)),
                radius=0.0,
            ),
            Rectangle(
                visible=True,
                origin=(0.0, 0.0),
                rotation=0.0,
                line_color=(64, 64, 64),
                fill_color=(192, 192, 192),
                pattern=LinePattern.SOLID,
                fill_pattern=FillPattern.HORIZONTAL_CYLINDER,
                line_thickness=0.25,
                border_pattern=BorderPattern.NONE,
                extent=((50.0, -10.0), (100.0, 10.0)),
                radius=0.0,
            ),
            Line(
                visible=True,
                origin=(0.0, 0.0),
                rotation=0.0,
                points=[(-80.0, -25.0), (-60.0, -25.0)],
                color=(0, 0, 0),
                pattern=LinePattern.SOLID,
                thickness=0.25,
                arrow=(Arrow.NONE, Arrow.NONE),
                arrow_size=3.0,
                smooth=Smooth.NONE,
            ),
            Text(
                visible=True,
                origin=(0.0, 0.0),
                rotation=0.0,
                extent=((-150.0, 60.0), (150.0, 100.0)),
                string="%name",
                font_size=0.0,
                font_name="",
                text_style=[],
                text_color=(0, 0, 0),
                horizontal_alignment=TextAlignment.CENTER,
                index=0,
            ),
        ],
    )
    parsed_icon = parse_icon_annotation(annotation_string)
    assert parsed_icon == expected


def test_parse_placement_annotation():
    s = "{Placement(true,-,-,32.0,-20.0,52.0,0.0,-,-,-,-,-,-,-,-),SomeOther(),ignoreThis=5}"
    placement = parse_placement_annotation(s)
    assert isinstance(placement, Placement)
    assert placement.visible is True
    assert placement.transformation.origin == (0.0, 0.0)
    assert placement.transformation.extent == ((32.0, -20.0), (52.0, 0.0))
    assert placement.transformation.rotation == 0.0
    assert placement.icon_transformation.origin == (0.0, 0.0)
    assert placement.icon_transformation.extent == (
        (-100.0, -100.0),
        (100.0, 100.0),
    )
    assert placement.icon_transformation.rotation == 0.0


def test_parse_placement_annotation_defaults():
    s = "{Placement(-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-)}"
    placement = parse_placement_annotation(s)
    assert isinstance(placement, Placement)
    assert placement.visible is True
    assert placement.transformation.origin == (0.0, 0.0)
    assert placement.transformation.extent == ((-100.0, -100.0), (100.0, 100.0))
    assert placement.transformation.rotation == 0.0
    assert placement.icon_transformation.origin == (0.0, 0.0)
    assert placement.icon_transformation.extent == (
        (-100.0, -100.0),
        (100.0, 100.0),
    )
    assert placement.icon_transformation.rotation == 0.0
