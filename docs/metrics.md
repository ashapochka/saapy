From [JarAnalyzer](http://www.kirkk.com/main/Main/JarAnalyzer)

**Number of Classes**
The number of concrete and abstract classes (and interfaces) in the jar is an indicator of the extensibility of the jar.

**Number of Packages**
The number of packages in the jar.

**Level**
The Level represents where in the hierarchy a jar file lives. Level 1 jars are at the bottom. Level 2 depend on at least one Level 1. Level 3 depend on at least one Level 2. The Level of the jar, used in conjunction with Instability, gives an indication of the jar's resilience to change.

**Afferent Couplings**
The number of other jars that depend upon classes within the jar is an indicator of the jar's responsibility.

**Efferent Couplings**
The number of other jars that the classes in the jar depend upon is an indicator of the jar's independence.

**Abstractness**
The ratio of the number of abstract classes (and interfaces) in the analyzed jar to the total number of classes in the analyzed jar.

The range for this metric is 0 to 1, with A=0 indicating a completely concrete jar and A=1 indicating a completely abstract jar.

**Instability**
The ratio of efferent coupling (Ce) to total coupling (Ce / (Ce + Ca)). This metric is an indicator of the jar's resilience to change.

The range for this metric is 0 to 1, with I=0 indicating a completely stable jar and I=1 indicating a completely instable jar.

**Distance**
The perpendicular distance of a jar from the idealized line A + I = 1. This metric is an indicator of the jar's balance between abstractness and stability.

A jar squarely on the main sequence is optimally balanced with respect to its abstractness and stability. Ideal jars are either completely abstract and stable (x=0, y=1) or completely concrete and instable (x=1, y=0).

The range for this metric is 0 to 1, with D=0 indicating a jar that is coincident with the main sequence and D=1 indicating a jar that is as far from the main sequence as possible.

**Unresolved Packages**
Packages not found in any of the jars analyzed. These can be filtered from output by specifying the packages to exlude in the Filter.properties file. Conversely, you can include jars containing these packages in the directory being analyzed.

These packages are excluded from all calculations and adding the jars containing these packages will result in modified metrics.
