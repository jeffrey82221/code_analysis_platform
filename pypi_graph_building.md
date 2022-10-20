# Steps of Data Loading

1. extract pypi package names:
```
python crawl_pkg_names.py
```
2. extract package dependencies:
```
python crawl_pkg_deps.py
```
3. build package dependency edge csv:
```
python build_dep_csv.py
```
4. build node csv:
```
python build_pkg_csv.py
```
5. bulk insert csv into redisgraph:

5.1. start graph db: 
```
redis-stack-server --port 9001
```
5.2. install bulk insert toolkit
```
pip install redisgraph-bulk-loader
redisgraph-bulk-insert DGraph -h 127.0.0.1 -p 9001 -n pkg.csv -r dep_edge.csv
```
If DGraph already exists, flush the redis-stack-server to clean up all data
```
redis-cli -h localhost -p 9001
> 
FLUSHALL
```

# EDA 

## Enter the cli terminal 
```
redis-cli -h localhost -p 9001
```
## Understand the Graph structure 
```
GRAPH.QUERY DGraph "MATCH ()-[r]-() RETURN DISTINCT type(r)"
```
## Understanding a Package 
### Find downstream packages of a package (e.g., smart-open) and Rank by popularity (in-degree):
```
GRAPH.QUERY DGraph "MATCH (n)-[]->(m) where m.name = 'smart-open' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 5"
```
```
GRAPH.QUERY DGraph "MATCH (n)-[]->(m) where m.name = 'ray' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 5"
```
```
GRAPH.QUERY DGraph "MATCH (n)-[]->(m) where m.name = 'neo4j-driver' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 5"
```
```
GRAPH.QUERY DGraph "MATCH (n)-[]->(m) where m.name = 'polars' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 5"
```
### Find upstream packages of a package (e.g., pandas) and Rank by popularity (in-degree):
```
GRAPH.QUERY DGraph "MATCH (m)-[r]->(n) where m.name = 'networkx-neo4j' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 10"
```
```
GRAPH.QUERY DGraph "MATCH (m)-[r]->(n) where m.name = 'pandas' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 10"
```
```
GRAPH.QUERY DGraph "MATCH (m)-[r]->(n) where m.name = 'johnnydep' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 10"
```
## Overall Analysis

### Finding the most popular package (highest in-degree)
```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, indegree(m) AS popularity ORDER BY popularity DESC LIMIT 10"
```
### Finding the package leveraging the large number of packages (dependency_degree)
```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, outdegree(m) AS dependency_degree ORDER BY dependency_degree DESC LIMIT 10"
```
### Package that is both popular and also leverage many other packages 
```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, outdegree(m)*indegree(m) AS smartness ORDER BY smartness DESC LIMIT 10"
```
### Finding the package that is high in popularity with little dependency (importancy)

```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, indegree(m)/(1 + outdegree(m)) AS importance ORDER BY importance DESC LIMIT 20"
```

REF: https://redis.io/commands/graph.query/

