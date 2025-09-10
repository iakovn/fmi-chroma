from collections.abc import Sequence

from .types import (
    Color,
    Ellipse,
    GraphicObject,
    Icon,
    Line,
    Point,
    Polygon,
    Rectangle,
    Text,
)


def color_to_hex(color: Color) -> str:
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def point_to_str(point: Point) -> str:
    return f"{point[0]},{point[1]}"


def render_line(line: Line) -> str:
    points = " ".join(point_to_str(pt) for pt in line.points)
    return (
        f'<polyline points="{points}" '
        f'style="fill:none;stroke:{color_to_hex(line.color)};stroke-width:{line.thickness}" />'
    )


def render_polygon(polygon: Polygon) -> str:
    points = " ".join(point_to_str(pt) for pt in polygon.points)
    return (
        f'<polygon points="{points}" '
        f'style="fill:{color_to_hex(polygon.fill_color)};stroke:{color_to_hex(polygon.line_color)};stroke-width:{polygon.line_thickness}" />'
    )


def render_rectangle(rect: Rectangle) -> str:
    (x0, y0), (x1, y1) = rect.extent
    x = min(x0, x1)
    y = min(y0, y1)
    width = abs(x1 - x0)
    height = abs(y1 - y0)
    rx = rect.radius
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" '
        f'style="fill:{color_to_hex(rect.fill_color)};stroke:{color_to_hex(rect.line_color)};stroke-width:{rect.line_thickness}" />'
    )


def render_ellipse(ellipse: Ellipse) -> str:
    (x0, y0), (x1, y1) = ellipse.extent
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    rx = abs(x1 - x0) / 2
    ry = abs(y1 - y0) / 2
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
        f'style="fill:{color_to_hex(ellipse.fill_color)};stroke:{color_to_hex(ellipse.line_color)};stroke-width:{ellipse.line_thickness}" />'
    )


def render_text(text: Text) -> str:
    (x0, y0), (x1, y1) = text.extent
    x = (x0 + x1) / 2
    y = (y0 + y1) / 2
    font_size = text.font_size or 12
    fill = color_to_hex(text.text_color)
    align = {
        "Left": "start",
        "Center": "middle",
        "Right": "end",
    }.get(text.horizontal_alignment.name, "start")
    return f'<text x="{x}" y="{y}" font-size="{font_size}" fill="{fill}" text-anchor="{align}">{text.string}</text>'


def render_graphic(obj: GraphicObject) -> str:
    if isinstance(obj, Line):
        return render_line(obj)
    elif isinstance(obj, Polygon):
        return render_polygon(obj)
    elif isinstance(obj, Rectangle):
        return render_rectangle(obj)
    elif isinstance(obj, Ellipse):
        return render_ellipse(obj)
    elif isinstance(obj, Text):
        return render_text(obj)
    else:
        return ""


def icons_to_svg(icons: Sequence[Icon], filename: str | None = None) -> str:
    # Compute overall bounds
    min_x, min_y, max_x, max_y = 0, 0, 0, 0
    for icon in icons:
        (x0, y0), (x1, y1) = icon.coordinate_system.extent
        min_x = min(min_x, x0)
        min_y = min(min_y, y0)
        max_x = max(max_x, x1)
        max_y = max(max_y, y1)
    width = max_x - min_x
    height = max_y - min_y

    svg_elements = []
    for icon in icons:
        for obj in icon.graphics:
            svg_elements.append(render_graphic(obj))

    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="{min_x} {min_y} {width} {height}">\n'
        + "\n".join(svg_elements)
        + "\n</svg>"
    )

    if filename is not None:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg_content)
    return svg_content
