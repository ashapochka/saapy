### Git Queries

Create index on commit's hexsha:

```
CREATE INDEX ON :jpos_v5(hexsha)
```

Create parent relationships between commits based on hexsha:

```
MATCH (n:jpos_v5:GitCommit) 
WITH n MATCH (m:jpos_v5:GitCommit) 
WHERE m.hexsha in n.parents_hexsha 
CREATE (n)<-[r:Parent]-(m)
```

Find all commits with more than 1 parent:

```
MATCH (n:jpos_v5:GitCommit)-[r:Parent]->(m:jpos_v5:GitCommit) 
WITH COUNT(n) AS parent_count, m, COLLECT(n) as parents 
WHERE parent_count > 1 
RETURN m.message
```

Find initial commits with no parents:

```
MATCH (n:jpos_v3:GitCommit) 
WHERE SIZE(n.parents_hexsha) < 1 
RETURN n LIMIT 25
```

Find merge commits:

```
MATCH (n:jpos_v3:GitCommit) 
WHERE size(n.parents_hexsha) > 1 
RETURN n LIMIT 25
```

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
