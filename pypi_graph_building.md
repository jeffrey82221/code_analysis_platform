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
# EDA
```
redis-cli -h localhost -p 9001
```
```
GRAPH.QUERY DGraph "MATCH ()-[r]-() RETURN DISTINCT type(r)"
```
```
GRAPH.QUERY DGraph "MATCH (n)-[]->(k) WHERE n.name = 'pandas' RETURN k.name"
```
```
GRAPH.QUERY DGraph "MATCH (n) RETURN n.name, indegree(n) + outdegree(n) AS degree ORDER BY degree DESC LIMIT 10"
```
```
GRAPH.QUERY DGraph "MATCH (n) RETURN n.name, indegree(n) AS degree ORDER BY degree DESC LIMIT 10"
```
```
GRAPH.QUERY DGraph "MATCH (n) RETURN n.name, outdegree(n) AS degree ORDER BY degree DESC LIMIT 5"
```
```
GRAPH.QUERY DGraph "MATCH (n) RETURN n.name, indegree(n)/(1 + outdegree(n)) AS degree ORDER BY degree DESC LIMIT 10"
```
```
GRAPH.QUERY DGraph "MATCH (n) RETURN n.name, outdegree(n)/(1 + indegree(n)) AS degree ORDER BY degree DESC LIMIT 10"
```

REF: https://redis.io/commands/graph.query/

