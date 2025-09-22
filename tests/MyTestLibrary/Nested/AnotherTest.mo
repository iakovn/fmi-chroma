within MyTestLibrary.Nested;
model AnotherTest
    extends .Modelica.Blocks.Examples.PID_Controller;
    annotation(some="thing", other=123, __TestSpecification(p1=true, p2=2, p3="hello", p4=3.0));
end AnotherTest;
