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
python build_pkg_n_dep_csv.py
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
>>
	1) 1) "type(r)"
	2) 1) 1) "dep_edge"
	3) 1) "Cached execution: 0"
   		2) "Query internal execution time: 	826.638000 milliseconds"
	(0.83s)

## Understanding a Package 
### Find downstream packages of a package (e.g., smart-open) and Rank by popularity (in-degree):
```
GRAPH.QUERY DGraph "MATCH (n)-[]->(m) where m.name = 'smart-open' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 5"
```
>>
  	1) "gensim"
   	  2) (integer) 479
   	2) 1) "ray"
   	   2) (integer) 356
   	3) 1) "snakemake"
   	   2) (integer) 65
   	4) 1) "featuretools"
   	   2) (integer) 37
   	5) 1) "woodwork"
   	   2) (integer) 20
   	6) 1) "acryl-datahub"
   	   2) (integer) 15
   	7) 1) "pathy"
   	   2) (integer) 15
   	8) 1) "codefast"
   	   2) (integer) 14
   	9) 1) "forte"
   	   2) (integer) 12

```
GRAPH.QUERY DGraph "MATCH (n)-[]->(m) where m.name = 'ray' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 5"
```
>> 
	1) 1) "transformers"
   	   2) (integer) 1017
  	2) 1) "pandera"
      2) (integer) 34
   	3) 1) "modin"
   	   2) (integer) 34
   	4) 1) "fugue"
   	   2) (integer) 19
   	5) 1) "alibi"
   	   2) (integer) 14

### Find upstream packages of a package (e.g., pandas) and Rank by popularity (in-degree):
```
GRAPH.QUERY DGraph "MATCH (m)-[r]->(n) where m.name = 'networkx-neo4j' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 10"
```
>> 
2) 1) 1) "neo4j-driver"
      2) (integer) 30
      
```
GRAPH.QUERY DGraph "MATCH (m)-[r]->(n) where m.name = 'pandas' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 10"
```

>>
	1) 1) "numpy"
  	   2) (integer) 33849
  	2) 1) "pytest"
  	   2) (integer) 21222
  	3) 1) "python-dateutil"
  	   2) (integer) 6012
  	4) 1) "pytz"
  	   2) (integer) 3321
  	5) 1) "pytest-xdist"
  	   2) (integer) 1406
  	6) 1) "hypothesis"
  	   2) (integer) 815

```
GRAPH.QUERY DGraph "MATCH (m)-[r]->(n) where m.name = 'johnnydep' RETURN n.name, indegree(n) AS popularity ORDER BY popularity DESC LIMIT 10"
```
>>
    1) 1) "setuptools"
       2) (integer) 5642
    2) 1) "wheel"
       2) (integer) 4014
    3) 1) "colorama"
       2) (integer) 3322
    4) 1) "packaging"
       2) (integer) 2651
    5) 1) "tabulate"
       2) (integer) 2522
    6) 1) "toml"
       2) (integer) 2403
    7) 1) "pip"
       2) (integer) 1071
    8) 1) "cachetools"
       2) (integer) 649
    9) 1) "pkginfo"
       2) (integer) 306
       
## Overall Analysis

### Finding the most popular package (highest in-degree)
```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, indegree(m) AS popularity ORDER BY popularity DESC LIMIT 10"
```
>>
    1) 1) "numpy"
       2) (integer) 33849
    2) 1) "requests"
       2) (integer) 32526
    3) 1) "pandas"
       2) (integer) 21493
    4) 1) "pytest"
       2) (integer) 21222
    5) 1) "matplotlib"
       2) (integer) 14827
    6) 1) "scipy"
       2) (integer) 13976
    7) 1) "odoo"
       2) (integer) 12351
    8) 1) "click"
       2) (integer) 11012
    9) 1) "pytest-cov"
       2) (integer) 10093
       
### Finding the package leveraging the large number of packages (dependency_degree)
```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, outdegree(m) AS dependency_degree ORDER BY dependency_degree DESC LIMIT 10"
```
>>
    1) 1) "ai-python"
       2) (integer) 2462
    2) 1) "acryl-datahub"
       2) (integer) 2262
    3) 1) "apache-airflow"
       2) (integer) 1353
    4) 1) "custom-workflow-solutions"
       2) (integer) 1182
    5) 1) "pingpong-datahub"
       2) (integer) 934
    6) 1) "apache-airflow-zack"
       2) (integer) 876
    7) 1) "boto3-stubs-lite"
       2) (integer) 646
    8) 1) "boto3-stubs"
       2) (integer) 646
    9) 1) "types-aiobotocore-lite"
       2) (integer) 637
       
### Package that is both popular and also leverage many other packages 
```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, outdegree(m)*indegree(m) AS smartness ORDER BY smartness DESC LIMIT 10"
```
>>
	1) 1) "apache-airflow"
       2) (integer) 531729
    2) 1) "transformers"
       2) (integer) 338661
    3) 1) "pytest"
       2) (integer) 318330
    4) 1) "scipy"
       2) (integer) 265544
    5) 1) "setuptools"
       2) (integer) 248248
    6) 1) "scikit-learn"
       2) (integer) 209344
    7) 1) "sphinx"
       2) (integer) 206816
    8) 1) "requests"
       2) (integer) 195156
    9) 1) "pandas"
       2) (integer) 150451
       
### Finding the package that is high in popularity with little dependency (importancy)

```
GRAPH.QUERY DGraph "MATCH (m) RETURN m.name, indegree(m)/(1 + outdegree(m)) AS importance ORDER BY importance DESC LIMIT 20"
```
>>
    1) 1) "numpy"
       2) "33849"
    2) 1) "matplotlib"
       2) "14827"
    3) 1) "odoo"
       2) "12351"
    4) 1) "six"
       2) "7709"
    5) 1) "pyyaml"
       2) "6181"
    6) 1) "PyYAML"
       2) "5573"
    7) 1) "requests"
       2) "4646.57142857143"
    8) 1) "Pillow"
       2) "3937"
    9) 1) "click"
       2) "3670.66666666667"
       
### Find important package via PageRank:
```
GRAPH.QUERY DGraph "CALL algo.pageRank('pkg', 'dep_edge') YIELD node, score RETURN node.name, score ORDER BY score DESC LIMIT 100"
```

>>
    1) 1) "pytest"
       2) "0.031449481844902"
    2) 1) "requests"
       2) "0.0230160858482122"
    3) 1) "odoo"
       2) "0.0185624267905951"
    4) 1) "numpy"
       2) "0.0181416310369968"
    5) 1) "importlib-metadata"
       2) "0.0159595292061567"
    6) 1) "six"
       2) "0.0145253213122487"
    7) 1) "tomli ;"
       2) "0.0111188208684325"
    8) 1) "typing-extensions"
       2) "0.0102907987311482"
    9) 1) "sphinx"
       2) "0.00911692064255476"


REF: https://redis.io/commands/graph.query/

