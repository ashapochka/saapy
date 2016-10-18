### Git Queries

Create index on git fields:

```
CREATE INDEX ON :GitCommit(hexsha)
CREATE INDEX ON :GitFileDiffStat(commit_hexsha)
CREATE INDEX ON :GitFileDiffStat(parent_hexsha)
CREATE INDEX ON :GitFileDiffStat(file_name)
```

Create parent relationships between commits based on hexsha:

```
MATCH (n:GitCommit) 
WITH n MATCH (m:GitCommit) 
WHERE m.hexsha in n.parents_hexsha 
CREATE (n)<-[r:Parent]-(m)
```

Find all commits with more than 1 parent:

```
MATCH (n:GitCommit)-[r:Parent]->(m:GitCommit) 
WITH COUNT(n) AS parent_count, m, COLLECT(n) as parents 
WHERE parent_count > 1 
RETURN m.message
```

Find initial commits with no parents:

```
MATCH (n:GitCommit) 
WHERE SIZE(n.parents_hexsha) < 1 
RETURN n LIMIT 25
```

Find merge commits:

```
MATCH (n:GitCommit) 
WHERE size(n.parents_hexsha) > 1 
RETURN n LIMIT 25
```

Create relationships between file diff stats and commits:

```
MATCH (file_diff:GitFileDiffStat)
WITH file_diff
MATCH (commit:GitCommit)
WHERE commit.hexsha = file_diff.commit_hexsha
WITH file_diff, commit
CREATE (commit)-[r:FileStats]->(file_diff)
```

Find large enough file changes not caused by merges:

```
MATCH (n:GitCommit)-->(m:GitFileDiffStat) 
WHERE m.file_name ENDS WITH ".java" 
AND size(n.parents_hexsha) = 1 
AND m.lines > 2 
RETURN n.authored_datetime, m.file_name, m.lines 
LIMIT 400
```

### Scitools Queries

Create indexes on typical scitools fields:

```
CREATE INDEX ON :ScitoolsEntity(ent_id)
CREATE INDEX ON :ScitoolsEntity(longname)
CREATE INDEX ON :ScitoolsEntity(kind_longname)
CREATE INDEX ON :ScitoolsEntity(uniquename)
CREATE INDEX ON :ScitoolsRef(scope_ent_id)
CREATE INDEX ON :ScitoolsRef(ent_id)
CREATE INDEX ON :ScitoolsRef(file_ent_id)
```

Find relative names of all files not in standard library:

```
MATCH (e:ScitoolsEntity) 
WHERE e.kind_longname CONTAINS "File" 
AND e.library <> "Standard" 
RETURN e.relname LIMIT 500
```

Label source files (as opposite to libraries):

```
MATCH (e:ScitoolsEntity) 
WHERE e.kind_longname CONTAINS "File" 
AND e.library <> "Standard" 
SET e:SourceFile
```

Index source file names:

```
CREATE INDEX ON :SourceFile(relname)
```

Create relationships between git file diff stats and source files:

```
MATCH (ent:SourceFile) 
WITH ent 
MATCH (diff:GitFileDiffStat) 
WHERE ent.relname = diff.file_name 
WITH ent, diff 
CREATE (ent)-[r:FileDiffStats]->(diff)
```

Select source files with most changes and some metrics:

```
MATCH (e:SourceFile)-->(d:GitFileDiffStat) 
WITH e, COUNT(d) as diff_count 
ORDER BY diff_count DESC 
RETURN diff_count, e.relname, e.metric_CountLineCode, 
e.metric_AvgCyclomatic, e.metric_MaxCyclomatic, e.metric_SumCyclomatic 
LIMIT 100
```

Label packages (Java):

```
MATCH (n:ScitoolsEntity) 
WHERE n.kind_longname 
CONTAINS "Package" 
SET n:Package
```

Find references from source files to packages:

```
MATCH (f:SourceFile)-->(r:ScitoolsRef)-->(p:Package) 
WHERE p.library <> "Standard" 
AND r.kind_longname <> "Java Declare" 
AND r.kind_longname <> "Java Define" 
RETURN f.relname, r.kind_longname, p.longname 
LIMIT 200
```

Find source files implementing packages:

```
MATCH (f:SourceFile)-[:Scopes]->(r:ScitoolsRef)-[:Refs]->(p:Package) 
WHERE r.kind_longname = "Java Define" 
RETURN f.relname, p.longname
```

Find library packages which are not part of JDK:

```
MATCH (p:Package) 
WHERE p.library = "Standard" 
AND NOT(p.longname STARTS with "java" 
OR p.longname STARTS WITH "sun" 
OR p.longname STARTS WITH "com.sun") 
RETURN p.longname ORDER BY p.longname
```

Find source files directly using osgi:

```
MATCH (f:SourceFile)-->(r:ScitoolsRef)-->(p:Package) 
WHERE p.longname STARTS WITH "org.osgi" 
AND r.kind_longname <> "Java Declare" 
AND r.kind_longname <> "Java Define" 
RETURN f.relname, r.kind_longname, p.longname
```

Use unwind to do node matches in batch (like join)

```
UNWIND [
{author_name: "Andres Alcarraz"}, 
{author_name: "Barzilai Spinak"}] 
AS map 
MATCH (a:GitAuthor {author_name: map.author_name})
MATCH (c:GitCommit {author_name: map.author_name})
RETURN a.author_email, c.hexsha, c.message
```

Find commits by people who are not represented by multiple different git names/emails

```
MATCH (a:GitAuthor) 
WHERE NOT (a:GitAuthor)-[:Similar]->(:GitAuthor) AND
NOT (:GitAuthor)-[:Similar]->(a:GitAuthor)
WITH a
MATCH p=(a)-[:Authors]->(c:GitCommit)
RETURN COUNT(p)
```

Commit stats by actor:

```
MATCH (actor:Actor:analysis)-->(a:GitAuthor:git)-->(c:GitCommit:git) 
RETURN actor.name AS actor_name, COUNT(DISTINCT c.hexsha) AS commit_count 
ORDER BY commit_count DESC
```

Commit stats by actor without merges:

```
MATCH (actor:Actor:analysis)-->(a:GitAuthor:git)-->(c:GitCommit:git) 
WHERE SIZE(c.parents_hexsha) < 2
RETURN actor.name AS actor_name, COUNT(DISTINCT c.hexsha) AS commit_count 
ORDER BY commit_count DESC
```

Commit stats for each account belonging to same actor:

```
MATCH (actor:Actor:analysis {name: "Robert Demski"})-->(a:GitAuthor:git)
WITH a
MATCH (a)-->(c:GitCommit:git) 
WHERE SIZE(c.parents_hexsha) < 2
RETURN a.author_name AS name, a.author_email AS email, COUNT(DISTINCT c.hexsha) AS commit_count 
ORDER BY commit_count DESC
```

Package change stats by actor:

```
MATCH (actor:Actor:analysis)-->(author:GitAuthor:git)-->(commit:GitCommit)-[:FileStats]->(diff:GitFileDiffStat)<-[:FileDiffStats]-(file:SourceFile)-[:Scopes]->(ref:ScitoolsRef)-[:Refs]->(package:Package) 
WHERE ref.kind_longname = "Java Define" AND
SIZE(commit.parents_hexsha) < 2 
RETURN 
actor.name AS actor_name,
SUM(diff.lines) AS lines_sum,
package.longname AS package_name, 
COUNT(DISTINCT file.relname) AS source_file_count
ORDER BY actor_name, lines_sum DESC
```

Find dependencies between packages:

```
MATCH (f:SourceFile)-[:Scopes]->(define:ScitoolsRef)-[:Refs]->(p_def:Package) 
WHERE define.kind_longname = "Java Define" 
WITH f, p_def
MATCH (f)-->(use:ScitoolsRef)-->(p_use:Package) 
WHERE p_use.library <> "Standard" 
AND use.kind_longname <> "Java Declare" 
AND use.kind_longname <> "Java Define" 
RETURN DISTINCT p_def.longname AS from_package, 
p_use.longname AS to_package,
COUNT(DISTINCT f) as file_number, COLLECT(DISTINCT f.relname) 
ORDER BY from_package, to_package
```

Create dependencies between packages:

```
MATCH (f:SourceFile)-[:Scopes]->(define:ScitoolsRef)-[:Refs]->(p_def:Package) 
WHERE define.kind_longname = "Java Define" 
WITH f, p_def
MATCH (f)-->(use:ScitoolsRef)-->(p_use:Package) 
WHERE p_use.library <> "Standard" 
AND use.kind_longname <> "Java Declare" 
AND use.kind_longname <> "Java Define" 
WITH DISTINCT p_def, p_use,
COUNT(DISTINCT f) as dependent_file_count, COLLECT(DISTINCT f.relname) AS dependent_files
CREATE (p_def)-[dep:Depends {dependent_file_count: dependent_file_count, dependent_files: dependent_files}]->(p_use)
```

Create work relationships between authors and packages

```
MATCH (actor:Actor:analysis)-->(author:GitAuthor:git)-->(commit:GitCommit)-[:FileStats]->(diff:GitFileDiffStat)<-[:FileDiffStats]-(file:SourceFile)-[:Scopes]->(ref:ScitoolsRef)-[:Refs]->(package:Package) 
WHERE ref.kind_longname = "Java Define" AND
SIZE(commit.parents_hexsha) < 2 
WITH 
actor,
SUM(diff.lines) AS lines_sum,
package, 
COUNT(DISTINCT file.relname) AS source_file_count
CREATE (actor)-[w:Modifies {lines_sum: lines_sum, source_file_count: source_file_count}]->(package)
```

Determine who develops packages and who uses them:

```
MATCH (a1:Actor)-->(p1:Package)<--(p2:Package)<--(a2:Actor)
RETURN DISTINCT p1.longname AS base_package, 
COLLECT(DISTINCT a1.name) AS p1_authors, p2.longname AS dependent_package, 
COLLECT(DISTINCT a2.name) AS p2_authors
ORDER BY base_package, dependent_package
```

Determine how many actors who did not develop specific packages use them:

```
MATCH (a1:Actor)-->(p1:Package)<--(p2:Package)<--(a2:Actor)
WITH DISTINCT p1.longname AS package, 
COLLECT(DISTINCT a1.name) AS developers, 
COLLECT(DISTINCT a2.name) AS users
RETURN package, 
SIZE(developers) AS developer_count,
SIZE(FILTER(user IN users WHERE NOT user IN developers)) AS user_count
ORDER BY user_count, package
```

Same as before with the travis CI server filtered out:

```
MATCH (a1:Actor)-->(p1:Package)<--(p2:Package)<--(a2:Actor)
WHERE NOT "Travis" IN [a1.name, a2.name]
WITH DISTINCT p1.longname AS package, 
COLLECT(DISTINCT a1.name) AS developers, COLLECT(DISTINCT a2.name) AS users
RETURN package, 
SIZE(developers) AS developer_count,
SIZE(FILTER(user IN users WHERE NOT user IN developers)) AS user_count
ORDER BY user_count, package
```

Adding some metrics:

```
MATCH (a1:Actor)-->(p1:Package)<--(p2:Package)<--(a2:Actor)
WHERE NOT "Travis" IN [a1.name, a2.name]
WITH DISTINCT p1.longname AS package, p1.metric_CountDeclClass AS class_count,
p1.metric_CountDeclMethodPublic AS public_method_count,
p1.metric_SumCyclomaticStrict AS total_cyclomatic_strict,
COLLECT(DISTINCT a1.name) AS developers, COLLECT(DISTINCT a2.name) AS users,
COLLECT(DISTINCT p2.longname) AS dependent_packages
RETURN package, class_count, public_method_count, total_cyclomatic_strict,
SIZE(developers) AS developer_count,
SIZE(FILTER(user IN users WHERE NOT user IN developers)) AS user_count,
SIZE(dependent_packages) AS dependency_count
ORDER BY user_count DESC, total_cyclomatic_strict DESC
```

List commit history for actors:

```
MATCH (c:jpos:GitCommit)<--(ga:jpos:GitAuthor)<--(a:jpos:Actor)
WHERE SIZE(c.parents_hexsha) < 2
WITH c, a
RETURN c.authored_date AS commit_date, c.authored_datetime AS commit_datetime, a.name AS commit_author
ORDER BY commit_date
```
