within MyTestLibrary;
package Nested

model PID2
  .Modelica.Blocks.Continuous.PID pid1(k=1, Ti=1, Td=0.1);
  .Modelica.Blocks.Continuous.PID pid2(k=2, Ti=2, Td=0.1);
  parameter Real x = 0.5;
end PID2;

model TestPID
    extends .Modelica.Blocks.Examples.PID_Controller;
    annotation(some="thing", other=123, __TestSpecification(p1=true, p2=2, p3="hello", p4=3.0));
end TestPID;

end Nested;
