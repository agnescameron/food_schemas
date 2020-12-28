## Collections in neo4j format

Collections should be formatted as folders, named for the date they were generated (in the format mm_dd_yy). For days where more than 1 version is produced, name is mm_dd_yy-number, with numbers starting at 1.

Each folder should contain the meta-schema, generated for that version, plus an exported Neo4j file. This file may be exported from a neo4j database (with the APOC plugin installed and file exports enabled in `neo4j.conf`), using the cypher command:

```
CALL apoc.export.csv.all('recipes.csv', {})
```

Each collection may also contain a readme, giving an overview of what that version contains.

For an example, check out 12_28_20.