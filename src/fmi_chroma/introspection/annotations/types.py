from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated

# --- Enumerations ---


class LinePattern(Enum):
    NONE = "None"
    SOLID = "Solid"
    DASH = "Dash"
    DOT = "Dot"
    DASH_DOT = "DashDot"
    DASH_DOT_DOT = "DashDotDot"


class FillPattern(Enum):
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
    NONE = "None"
    RAISED = "Raised"
    SUNKEN = "Sunken"
    ENGRAVED = "Engraved"


class Smooth(Enum):
    NONE = "None"
    BEZIER = "Bezier"


class Arrow(Enum):
    NONE = "None"
    OPEN = "Open"
    FILLED = "Filled"
    HALF = "Half"


class TextStyle(Enum):
    BOLD = "Bold"
    ITALIC = "Italic"
    UNDERLINE = "UnderLine"


class TextAlignment(Enum):
    LEFT = "Left"
    CENTER = "Center"
    RIGHT = "Right"


class EllipseClosure(Enum):
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
    visible: bool = True
    origin: Point = (0.0, 0.0)
    rotation: Annotated[float, "degrees"] = 0.0


@dataclass
class FilledShape:
    line_color: Color = BLACK
    fill_color: Color = BLACK
    pattern: LinePattern = LinePattern.SOLID
    fill_pattern: FillPattern = FillPattern.NONE
    line_thickness: DrawingUnit = 0.25


# --- Transformation and Placement ---


@dataclass
class Transformation:
    extent: Extent = ((-100.0, -100.0), (100.0, 100.0))
    rotation: Annotated[float, "degrees"] = 0.0
    origin: Point = (0.0, 0.0)


@dataclass
class Placement:
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
    points: list[Point] = field(default_factory=list)
    color: Color = BLACK
    pattern: LinePattern = LinePattern.SOLID
    thickness: DrawingUnit = 0.25
    arrow: tuple[Arrow, Arrow] = (Arrow.NONE, Arrow.NONE)
    arrow_size: DrawingUnit = 3.0
    smooth: Smooth = Smooth.NONE


@dataclass
class Polygon(GraphicItem, FilledShape):
    points: list[Point] = field(default_factory=list)
    smooth: Smooth = Smooth.NONE


@dataclass
class Rectangle(FilledShape, GraphicItem):
    border_pattern: BorderPattern = BorderPattern.NONE
    extent: Extent = field(
        default_factory=lambda: ((-100.0, -100.0), (100.0, 100.0))
    )
    radius: DrawingUnit = 0.0


@dataclass
class Ellipse(FilledShape, GraphicItem):
    extent: Extent = field(
        default_factory=lambda: ((-100.0, -100.0), (100.0, 100.0))
    )
    start_angle: Annotated[float, "degrees"] = 0.0
    end_angle: Annotated[float, "degrees"] = 360.0
    closure: EllipseClosure = EllipseClosure.CHORD


@dataclass
class Text(GraphicItem):
    extent: Extent = field(
        default_factory=lambda: ((-100.0, -100.0), (100.0, 100.0))
    )
    string: str = ""
    font_size: Annotated[float, "pt"] = 0.0
    font_name: str = ""
    text_style: list[TextStyle] = field(default_factory=list)
    text_color: Color = BLACK
    horizontal_alignment: TextAlignment = TextAlignment.LEFT
    index: int = 0


# --- Top-Level Icon and Coordinate System ---


@dataclass
class CoordinateSystem:
    extent: Extent = ((-100.0, -100.0), (100.0, 100.0))
    preserve_aspect_ratio: bool = True
    initial_scale: float = 0.1
    grid: tuple[DrawingUnit, DrawingUnit] = (1.0, 1.0)


GraphicObject = Line | Polygon | Rectangle | Ellipse | Text


@dataclass
class Icon:
    coordinate_system: CoordinateSystem
    graphics: list[GraphicObject]


# --- Component Information ---


class Variability(Enum):
    CONSTANT = "constant"
    PARAMETER = "parameter"
    DISCRETE = "discrete"
    UNSPECIFIED = "unspecified"


@dataclass
class Component:
    type: str
    name: str
    description: str
    access: str
    is_final: bool
    is_flow: bool
    is_stream: bool
    is_replaceable: bool
    variability: Variability
    is_inner: bool
    is_outer: bool
    direction: str
    array_dimensions: list[int] = field(default_factory=list)
