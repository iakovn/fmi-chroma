"""
This module provides Python dataclass mappings for Modelica graphical
annotation records, based on the OpenModelica API introspection.
"""

from lark import Lark, Transformer

from .types import (
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
    TextStyle,
    Transformation,
)

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


PLACEMENT_GRAMMAR = r"""
    ?start: annotations

    annotations : "{" [annotation ("," annotation)*] "}"
    placement : "Placement" "(" fields ")"

    other : /(?!(Placement))[^,{}]+/   // matches any other annotation, ignored
    annotation : placement
              | other
    fields : field ("," field)* [","]
    field : "true"    -> true
          | "false"   -> false
          | SIGNED_NUMBER -> number
          | "-"      -> default_value


    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""


class PlacementTransformer(Transformer):
    def true(self, _):
        return True

    def false(self, _):
        return False

    def number(self, n):
        # n may be a Token or a list if the grammar is ambiguous
        if isinstance(n, list):
            n = n[0]
        return float(n)

    def default_value(self, _):
        return None

    def fields(self, fields):
        # Flatten any nested lists (from ambiguous parses)
        flat_fields = []
        for f in fields:
            if isinstance(f, list):
                flat_fields.extend(f)
            else:
                flat_fields.append(f)
        fields = flat_fields
        # Remove any trailing None caused by an extra comma
        if len(fields) > 15:
            fields = fields[:15]
        if len(fields) != 15:
            raise ValueError(  # noqa: TRY003
                f"Expected 15 fields for Placement, got {len(fields)}"
            )
        visible = fields[0] if fields[0] is not None else True
        origin_x = fields[1] if fields[1] is not None else 0.0
        origin_y = fields[2] if fields[2] is not None else 0.0
        extent_x1 = fields[3] if fields[3] is not None else -100.0
        extent_y1 = fields[4] if fields[4] is not None else -100.0
        extent_x2 = fields[5] if fields[5] is not None else 100.0
        extent_y2 = fields[6] if fields[6] is not None else 100.0
        rotation = fields[7] if fields[7] is not None else 0.0

        icon_origin_x = fields[8] if fields[8] is not None else 0.0
        icon_origin_y = fields[9] if fields[9] is not None else 0.0
        icon_extent_x1 = fields[10] if fields[10] is not None else -100.0
        icon_extent_y1 = fields[11] if fields[11] is not None else -100.0
        icon_extent_x2 = fields[12] if fields[12] is not None else 100.0
        icon_extent_y2 = fields[13] if fields[13] is not None else 100.0
        icon_rotation = fields[14] if fields[14] is not None else 0.0

        transformation = Transformation(
            origin=(origin_x, origin_y),
            extent=((extent_x1, extent_y1), (extent_x2, extent_y2)),
            rotation=rotation,
        )
        icon_transformation = Transformation(
            origin=(icon_origin_x, icon_origin_y),
            extent=(
                (icon_extent_x1, icon_extent_y1),
                (icon_extent_x2, icon_extent_y2),
            ),
            rotation=icon_rotation,
        )
        return {
            "visible": visible,
            "transformation": transformation,
            "icon_transformation": icon_transformation,
        }

    def placement(self, children):
        return Placement(**children[0])

    def annotation(self, children):
        if children and isinstance(children[0], Placement):
            return children[0]
        return None

    def annotations(self, children):
        for child in children:
            if isinstance(child, Placement):
                return child
        return None


placement_parser = Lark(
    PLACEMENT_GRAMMAR,
    start="annotations",
    parser="lalr",
    transformer=PlacementTransformer(),
)


def parse_placement_annotation(annotation_string: str) -> Placement | None:
    """
    Parses a Modelica component annotation string and returns the Placement annotation as a Placement object.
    Returns None if not found or parsing fails.
    """
    try:
        return placement_parser.parse(annotation_string)
    except Exception as e:
        print(f"Failed to parse Placement annotation: {e}")
        return None
