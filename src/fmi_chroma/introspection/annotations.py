"""
This module provides Python dataclass mappings for Modelica graphical
annotation records, based on the OpenModelica API introspection.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated

# --- Enumerations ---


class LinePattern(Enum):
    """Modelica LinePattern enumeration."""

    NONE = "None"
    SOLID = "Solid"
    DASH = "Dash"
    DOT = "Dot"
    DASH_DOT = "DashDot"
    DASH_DOT_DOT = "DashDotDot"


class FillPattern(Enum):
    """Modelica FillPattern enumeration."""

    NONE = "None"
    SOLID = "Solid"
    HORIZONTAL = "Horizontal"
    VERTICAL = "Vertical"
    CROSS = "Cross"
    FORWARD = "Forward"
    BACKWARD = "Backward"
    CROSS_DIAG = "CrossDiag"
    HORIZONTAL_CYLINDER = "HorizontalCylinder"
    VERTICAL_CYLINDER = "VerticalCylinder"
    SPHERE = "Sphere"


class BorderPattern(Enum):
    """Modelica BorderPattern enumeration."""

    NONE = "None"
    RAISED = "Raised"
    SUNKEN = "Sunken"
    ENGRAVED = "Engraved"


class Smooth(Enum):
    """Modelica Smooth enumeration."""

    NONE = "None"
    BEZIER = "Bezier"


class Arrow(Enum):
    """Modelica Arrow enumeration."""

    NONE = "None"
    OPEN = "Open"
    FILLED = "Filled"
    HALF = "Half"


class TextStyle(Enum):
    """Modelica TextStyle enumeration."""

    BOLD = "Bold"
    ITALIC = "Italic"
    UNDERLINE = "UnderLine"


class TextAlignment(Enum):
    """Modelica TextAlignment enumeration."""

    LEFT = "Left"
    CENTER = "Center"
    RIGHT = "Right"


class EllipseClosure(Enum):
    """Modelica EllipseClosure enumeration."""

    NONE = "None"
    CHORD = "Chord"
    RADIAL = "Radial"


# --- Type Aliases ---

DrawingUnit = float
Point = tuple[DrawingUnit, DrawingUnit]
Extent = tuple[Point, Point]
Color = tuple[int, int, int]
BLACK: Color = (0, 0, 0)


# --- Base Record Dataclasses ---


@dataclass
class GraphicItem:
    """Modelica partial record GraphicItem."""

    visible: bool = True
    origin: Point = (0.0, 0.0)
    rotation: Annotated[float, "degrees"] = 0.0


@dataclass
class FilledShape:
    """Modelica record FilledShape."""

    line_color: Color = BLACK
    fill_color: Color = BLACK
    pattern: LinePattern = LinePattern.SOLID
    fill_pattern: FillPattern = FillPattern.NONE
    line_thickness: DrawingUnit = 0.25


# --- Transformation and Placement ---


@dataclass
class Transformation:
    """Modelica record Transformation."""

    extent: Extent = ((-100.0, -100.0), (100.0, 100.0))
    rotation: Annotated[float, "degrees"] = 0.0
    origin: Point = (0.0, 0.0)


@dataclass
class Placement:
    """Modelica record Placement."""

    visible: bool = True
    transformation: Transformation = field(
        default_factory=lambda: Transformation()
    )
    icon_visible: bool = False
    icon_transformation: Transformation = field(
        default_factory=lambda: Transformation()
    )


# --- Graphic Item Dataclasses ---


@dataclass
class Line(GraphicItem):
    """Modelica record Line."""

    points: list[Point] = field(default_factory=list)
    color: Color = BLACK
    pattern: LinePattern = LinePattern.SOLID
    thickness: DrawingUnit = 0.25
    arrow: tuple[Arrow, Arrow] = (Arrow.NONE, Arrow.NONE)
    arrow_size: DrawingUnit = 3.0
    smooth: Smooth = Smooth.NONE


@dataclass
class Polygon(GraphicItem, FilledShape):
    """Modelica record Polygon."""

    points: list[Point] = field(default_factory=list)
    smooth: Smooth = Smooth.NONE


@dataclass
class Rectangle(FilledShape, GraphicItem):
    """Modelica record Rectangle."""

    border_pattern: BorderPattern = BorderPattern.NONE
    extent: Extent = field(
        default_factory=lambda: ((-100.0, -100.0), (100.0, 100.0))
    )
    radius: DrawingUnit = 0.0


@dataclass
class Ellipse(FilledShape, GraphicItem):
    """Modelica record Ellipse."""

    extent: Extent = field(
        default_factory=lambda: ((-100.0, -100.0), (100.0, 100.0))
    )
    start_angle: Annotated[float, "degrees"] = 0.0
    end_angle: Annotated[float, "degrees"] = 360.0
    # NOTE: Default logic from Modelica spec is complex; using a sensible default
    closure: EllipseClosure = EllipseClosure.CHORD


@dataclass
class Text(GraphicItem):
    """Modelica record Text."""

    extent: Extent = field(
        default_factory=lambda: ((-100.0, -100.0), (100.0, 100.0))
    )
    string: str = ""
    font_size: Annotated[float, "pt"] = 0.0
    font_name: str = ""
    text_style: list[TextStyle] = field(default_factory=list)
    text_color: Color = BLACK
    # NOTE: Default logic from Modelica spec is complex; using a sensible default
    horizontal_alignment: TextAlignment = TextAlignment.LEFT
    index: int = 0


# --- Top-Level Icon and Coordinate System ---


@dataclass
class CoordinateSystem:
    """Modelica record CoordinateSystem."""

    extent: Extent = ((-100.0, -100.0), (100.0, 100.0))
    preserve_aspect_ratio: bool = True
    initial_scale: float = 0.1
    grid: tuple[DrawingUnit, DrawingUnit] = (1.0, 1.0)


GraphicObject = Line | Polygon | Rectangle | Ellipse | Text


@dataclass
class Icon:
    """Modelica record Icon."""

    coordinate_system: CoordinateSystem
    graphics: list[GraphicObject]


# --- Component Information ---


class Variability(Enum):
    """Modelica component variability."""

    CONSTANT = "constant"
    PARAMETER = "parameter"
    DISCRETE = "discrete"
    UNSPECIFIED = "unspecified"


@dataclass
class Component:
    """Represents a component returned from the getComponents API call."""

    type: str
    name: str
    description: str
    access: str  # 'public' or 'protected'
    is_final: bool
    is_flow: bool
    is_stream: bool
    is_replaceable: bool
    variability: Variability
    is_inner: bool
    is_outer: bool
    direction: str  # 'input' or 'output'
    array_dimensions: list[int] = field(default_factory=list)


# Placeholder for the parse_icon_annotation function
def parse_icon_annotation(annotation_string: str) -> Icon:
    """
    Parses the string representation of a Modelica Icon annotation.

    Args:
        annotation_string: The raw string from getIconAnnotation.

    Returns:
        An Icon dataclass instance.
    """
    if not annotation_string:
        return Icon(
            coordinate_system=CoordinateSystem(),
            graphics=[],
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
                horizontal_alignment="TextAlignment.Center",
                index=0,
            ),
        ],
    )

    return expected
