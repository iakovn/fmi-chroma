## Model introspection with OpenModelica Python API

getComponents({model_name})
Returns list of components, each component as a tuple:
- type
- name
- description string
- public/protected
- final prefix
- flow prefix
- stream prefix
- replaceable prefix
- variability (constant/parameter/discrete/unspecified)
- inner/outer prefix
- input/output prefix
- array dimensions
----
getNthComponentAnnotation({model_name})
Retruns a string (expression), e.g.,:
  {Placement(true,-,-,60.0,-20.0,80.0,0.0,-,-,-,-,-,-,-,)}
  which should be parsed as an array of annotation records.

We focus on Placement:
record Placement
  Boolean visible = true;
  Transformation transformation "Placement in the diagram layer";
  Boolean iconVisible "Visible in icon layer; for public connector";
  Transformation iconTransformation
    "Placement in the icon layer; for public connector";
end Placement;
record Transformation
  Extent extent;
  Real rotation(quantity = "angle", unit = "deg") = 0;
  Point origin = {0, 0};
end Transformation;
type DrawingUnit = Real(final unit="mm");
type Point = DrawingUnit[2] "{x, y}";
type Extent = Point[2] "Defines a rectangular area {{x1, y1}, {x2, y2}}";

----
getIconAnnotation
Returns a string (expression), e.g.,
{-100.0,-100.0,100.0,100.0,true,-,-,,{Rectangle(true, {0.0, 0.0}, 0.0, {64, 64, 64}, {192, 192, 192}, LinePattern.Solid, FillPattern.HorizontalCylinder, 0.25, BorderPattern.None, {{-100.0, -10.0}, {-50.0, 10.0}}, 0.0), Rectangle(true, {0.0, 0.0}, 0.0, {64, 64, 64}, {192, 192, 192}, LinePattern.Solid, FillPattern.HorizontalCylinder, 0.25, BorderPattern.None, {{50.0, -10.0}, {100.0, 10.0}}, 0.0), Line(true, {0.0, 0.0}, 0.0, {{-80.0, -25.0}, {-60.0, -25.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{60.0, -25.0}, {80.0, -25.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{-70.0, -25.0}, {-70.0, -70.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{70.0, -25.0}, {70.0, -70.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{-80.0, 25.0}, {-60.0, 25.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{60.0, 25.0}, {80.0, 25.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{-70.0, 45.0}, {-70.0, 25.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{70.0, 45.0}, {70.0, 25.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Line(true, {0.0, 0.0}, 0.0, {{-70.0, -70.0}, {70.0, -70.0}}, {0, 0, 0}, LinePattern.Solid, 0.25, {Arrow.None, Arrow.None}, 3.0, Smooth.None), Rectangle(true, {0.0, 0.0}, 0.0, {64, 64, 64}, {255, 255, 255}, LinePattern.Solid, FillPattern.HorizontalCylinder, 0.25, BorderPattern.None, {{-50.0, -50.0}, {50.0, 50.0}}, 10.0), Text(true, {0.0, 0.0}, 0.0, {0, 0, 0}, {0, 0, 0}, LinePattern.Solid, FillPattern.None, 0.25, {{-150.0, 60.0}, {150.0, 100.0}}, "%name", 0.0, {0, 0, 255}, "", {}, TextAlignment.Center), Text(true, {0.0, 0.0}, 0.0, {0, 0, 0}, {0, 0, 0}, LinePattern.Solid, FillPattern.None, 0.25, {{-150.0, -120.0}, {150.0, -80.0}}, "J=%J", 0.0, {-1, -1, -1}, "", {}, TextAlignment.Center), Rectangle(true, {0.0, 0.0}, 0.0, {64, 64, 64}, {255, 255, 255}, LinePattern.Solid, FillPattern.None, 0.25, BorderPattern.None, {{-50.0, -50.0}, {50.0, 50.0}}, 10.0)}}

The expression needs to be parsed into:
record Icon "Representation of the icon layer"
  CoordinateSystem coordinateSystem(extent = {{-100, -100}, {100, 100}});
  GraphicItem[:] graphics;
end Icon;

record CoordinateSystem
  Extent extent;
  Boolean preserveAspectRatio = true;
  Real initialScale = 0.1;
  DrawingUnit grid[2];
end CoordinateSystem;

partial record GraphicItem
  Boolean visible = true;
  Point origin = {0, 0};
  Real rotation(quantity="angle", unit="deg")=0;
end GraphicItem;

Properties of graphical objects and connection lines are described using the following attribute types.

⬇
type Color = Integer[3](min = 0, max = 255) "RGB representation";
constant Color Black = zeros(3);
type LinePattern = enumeration(None, Solid, Dash, Dot, DashDot, DashDotDot);
type FillPattern = enumeration(None, Solid, Horizontal, Vertical,
                               Cross, Forward, Backward, CrossDiag,
                               HorizontalCylinder, VerticalCylinder, Sphere);
type BorderPattern = enumeration(None, Raised, Sunken, Engraved);
type Smooth = enumeration(None, Bezier);
type EllipseClosure = enumeration(None, Chord, Radial);

type Arrow = enumeration(None, Open, Filled, Half);
type TextStyle = enumeration(Bold, Italic, UnderLine);
type TextAlignment = enumeration(Left, Center, Right);
Filled shapes have the following attributes for the border and interior.

record FilledShape "Style attributes for filled shapes"
  Color lineColor = Black "Color of border line";
  Color fillColor = Black "Interior fill color";
  LinePattern pattern = LinePattern.Solid "Border line pattern";
  FillPattern fillPattern = FillPattern.None "Interior fill pattern";
  DrawingUnit lineThickness = 0.25 "Line thickness";
end FilledShape;
record Text
  extends GraphicItem;
  Extent extent;
  String string;
  Real fontSize = 0 "unit pt";
  String fontName;
  TextStyle textStyle[:];
  Color textColor = Color.Black;
  TextAlignment horizontalAlignment =
    if index < 0 then TextAlignment.Right else TextAligment.Left;
  Integer index;
end Text;
record Line
  extends GraphicItem;
  Point points[:];
  Color color = Black;
  LinePattern pattern = LinePattern.Solid;
  DrawingUnit thickness = 0.25;
  Arrow arrow[2] = {Arrow.None, Arrow.None} "{start arrow, end arrow}";
  DrawingUnit arrowSize = 3;
  Smooth smooth = Smooth.None "Spline";
end Line;
record Polygon
  extends GraphicItem;
  extends FilledShape;
  Point points[:];
  Smooth smooth = Smooth.None "Spline outline";
end Polygon;
record Rectangle
  extends GraphicItem;
  extends FilledShape;
  BorderPattern borderPattern = BorderPattern.None;
  Extent extent;
  DrawingUnit radius = 0 "Corner radius";
end Rectangle;
record Ellipse
  extends GraphicItem;
  extends FilledShape;
  Extent extent;
  Real startAngle(quantity = "angle", unit = "deg") = 0;
  Real endAngle(quantity = "angle", unit = "deg") = 360;
  EllipseClosure closure =
    if startAngle == 0 and endAngle == 360 then
      EllipseClosure.Chord
    else
      EllipseClosure.Radial;
end Ellipse;
