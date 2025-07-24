"""
This module provides Python dataclass mappings for Modelica graphical
annotation records, based on the OpenModelica API introspection.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated

from lark import Lark, Transformer

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


# --- Lark Grammar and Parser ---

ICON_GRAMMAR = r"""
    ?start: icon

    icon : "{" coordinate_system "," graphics "}"

    coordinate_system : SIGNED_NUMBER "," SIGNED_NUMBER "," SIGNED_NUMBER "," SIGNED_NUMBER "," boolean "," SIGNED_NUMBER "," [grid]
    grid : point

    graphics : "{" [graphic_item ("," graphic_item)*] "}"

    graphic_item : rectangle | line | text

    rectangle : "Rectangle(" boolean "," point "," SIGNED_NUMBER "," color "," color "," line_pattern "," fill_pattern "," SIGNED_NUMBER "," border_pattern "," extent "," SIGNED_NUMBER ")"
    line : "Line(" boolean "," point "," SIGNED_NUMBER "," points "," color "," line_pattern "," SIGNED_NUMBER "," arrow_pair "," SIGNED_NUMBER "," smooth ")"
    text : "Text(" boolean "," point "," SIGNED_NUMBER "," extent "," ESCAPED_STRING "," SIGNED_NUMBER "," ESCAPED_STRING "," text_style_list "," color "," text_alignment "," SIGNED_NUMBER ")"

    points : "{" [point ("," point)*] "}"
    extent : "{" point "," point "}"
    point : "{" SIGNED_NUMBER "," SIGNED_NUMBER "}"
    color : "{" SIGNED_NUMBER "," SIGNED_NUMBER "," SIGNED_NUMBER "}"
    arrow_pair : "{" arrow "," arrow "}"
    text_style_list : "{" [text_style ("," text_style)*] "}"

    boolean : "true" -> true | "false" -> false
    line_pattern : "LinePattern." WORD -> line_pattern
    fill_pattern : "FillPattern." WORD -> fill_pattern
    border_pattern : "BorderPattern." WORD -> border_pattern
    smooth : "Smooth." WORD -> smooth
    arrow : "Arrow." WORD -> arrow
    text_style : "TextStyle." WORD -> text_style
    text_alignment : "TextAlignment." WORD -> text_alignment

    %import common.WORD
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""


class IconTransformer(Transformer):
    """Transforms the Lark parse tree into annotation dataclasses."""

    def icon(self, children):
        return Icon(coordinate_system=children[0], graphics=children[1])

    def coordinate_system(self, children):
        return CoordinateSystem(
            extent=((children[0], children[1]), (children[2], children[3])),
            preserve_aspect_ratio=children[4],
            initial_scale=children[5] or 0.1,
            grid=children[6] or (1.0, 1.0),
        )

    def graphics(self, children):
        return children

    def graphic_item(self, children):
        return children[0]

    def rectangle(self, children):
        return Rectangle(
            line_color=children[3],
            fill_color=children[4],
            pattern=children[5],
            fill_pattern=children[6],
            line_thickness=children[7],
            visible=children[0],
            origin=children[1],
            rotation=children[2],
            border_pattern=children[8],
            extent=children[9],
            radius=children[10],
        )

    def line(self, children):
        return Line(
            visible=children[0],
            origin=children[1],
            rotation=children[2],
            points=children[3],
            color=children[4],
            pattern=children[5],
            thickness=children[6],
            arrow=children[7],
            arrow_size=children[8],
            smooth=children[9],
        )

    def text(self, children):
        return Text(
            visible=children[0],
            origin=children[1],
            rotation=children[2],
            extent=children[3],
            string=children[4],
            font_size=children[5],
            font_name=children[6],
            text_style=children[7],
            text_color=children[8],
            horizontal_alignment=children[9],
            index=children[10],
        )

    def points(self, children):
        return children

    def extent(self, children):
        return (children[0], children[1])

    def point(self, children):
        return (float(children[0]), float(children[1]))

    def color(self, children):
        return (int(children[0]), int(children[1]), int(children[2]))

    def arrow_pair(self, children):
        return (children[0], children[1])

    def text_style_list(self, children):
        return children if children[0] else []

    def line_pattern(self, children):
        return LinePattern(children[0].value)

    def fill_pattern(self, children):
        return FillPattern(children[0].value)

    def border_pattern(self, children):
        return BorderPattern(children[0].value)

    def smooth(self, children):
        return Smooth(children[0].value)

    def arrow(self, children):
        return Arrow(children[0].value)

    def text_style(self, children):
        return TextStyle(children[0].value)

    def text_alignment(self, children):
        return TextAlignment(children[0].value)

    def true(self, _):
        return True

    def false(self, _):
        return False

    def SIGNED_NUMBER(self, n):
        return float(n)

    def ESCAPED_STRING(self, s):
        return s[1:-1]


icon_parser = Lark(
    ICON_GRAMMAR, start="icon", parser="lalr", transformer=IconTransformer()
)


def parse_icon_annotation(annotation_string: str) -> Icon | None:
    """
    Parses the string representation of a Modelica Icon annotation using Lark.

    Args:
        annotation_string: The raw string from getIconAnnotation.

    Returns:
        An Icon dataclass instance or None if parsing fails.
    """
    try:
        # The annotation string can have an optional trailing comma in the graphics list
        clean_string = annotation_string.replace(",}}", "}}")
        return icon_parser.parse(clean_string)
    except Exception as e:
        print(f"Failed to parse annotation with Lark: {e}")
        return None
