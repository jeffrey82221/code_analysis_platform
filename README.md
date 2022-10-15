# code_analysis_platform
A playground for analyzing codebase using redisgraph and pycograph 


# Setup DB: 

1) Instal docker and run redisgraph & redisinsight

```
docker run -d -p 6379:6379 redislabs/redismod
docker run -d -v redisinsight:/db -p 8001:8001 redislabs/redisinsight:latest
```

NOTE: on mac: 

```
sudo chown -R $(whoami) /opt/homebrew
brew tap redis-stack/redis-stack
brew install redis-stack
redis-stack-server --port 9001
redis-cli -h localhost -p 9001
> ping
```
2) Install pycograph from source (hence we need to change the redis_port)

```
git clone https://github.com/jeffrey82221/pycograph.git
cd pycograph
pip install -r devtools/requirements.txt
pip install .
```

# Load Codes into RedisGraph via pycograph

1) git clone python standard library 

```
git clone https://github.com/python/cpython.git
cd cpython/Lib
```
2) import codes to redisgraph
```
pycograph load --project-dir .
```
>
```
Skipped module distutils.command.bdist_msi because of syntax error.
Skipped module test.badsyntax_3131 because of syntax error.
Skipped module test.bad_coding2 because of syntax error.
Skipped module test.test_importlib.test_util because of syntax error.
Skipped module lib2to3.tests.data.different_encoding because of syntax error.
Skipped module lib2to3.tests.data.false_encoding because of syntax error.
Skipped module lib2to3.tests.data.bom because of syntax error.
Skipped module lib2to3.tests.data.py2_test_grammar because of syntax error.
Skipped module lib2to3.tests.data.crlf because of syntax error.
Graph successfully updated.
{'graph name': '.', 'nodes added': 64762, 'edges added': 313360}
```

# Cypher-base EDA:

```
redis-cli -h localhost -p 9001
```
## what are the node properties (keys)? 
```
GRAPH.QUERY . "MATCH (n) RETURN DISTINCT keys(n)"
```
## what are the node types (label)?
```
GRAPH.QUERY . "MATCH (n) RETURN DISTINCT labels(n)"
```
## what is the number of nodes? 
```
GRAPH.QUERY . "MATCH (n) RETURN count(n)"
```
## what is the number of a specific type of nodes? 
```
GRAPH.QUERY . "MATCH (n: class) RETURN count(n)"
```
## what are the edges types?
```
GRAPH.QUERY . "MATCH ()-[r]-() RETURN DISTINCT type(r)"
```
## what are the number of edges of a specific type? 
```
GRAPH.QUERY . "MATCH ()-[r:imports]-() RETURN count(r)"
```
## what are the number of edges of a specific type linked between certain type of nodes? 
```
GRAPH.QUERY . "MATCH (a:module)-[r:imports]-(b:module) RETURN count(r)"
```

## Get degree of nodes given specific relationship

* First, we experience with finding the module 
that is popular in term of being imported 
```
GRAPH.QUERY . "MATCH (k:module) WITH k, size((:module)-[:imports]->(k:module)) as degree RETURN k.full_name, degree ORDER BY degree"
```
>>
```
...
   651) 1) "..socket"
        2) (integer) 11
   652) 1) "multiprocessing.reduction"
        2) (integer) 11
   653) 1) "..stat"
        2) (integer) 11
   654) 1) "asyncio.events"
        2) (integer) 12
   655) 1) "..functools"
        2) (integer) 12
   656) 1) "importlib.util"
        2) (integer) 13
   657) 1) "multiprocessing.util"
        2) (integer) 13
   659) 1) "..warnings"
        2) (integer) 21
   660) 1) "..io"
        2) (integer) 25
   ...
   662) 1) "distutils.log"
        2) (integer) 30
   663) 1) "..re"
        2) (integer) 37
   ...
   665) 1) "..os"
        2) (integer) 65
```

* Then, we experience with finding the module 
that import the largest amount of other modules
```
GRAPH.QUERY . "MATCH (k:module) WITH k, size((k:module)-[:imports]->(:module)) as degree RETURN k.full_name, degree ORDER BY degree"
```
>>
```
...
   662) 1) "..inspect"
        2) (integer) 13
   663) 1) "..pydoc"
        2) (integer) 14
   664) 1) "..pdb"
        2) (integer) 14
   665) 1) "idlelib.editor"
        2) (integer) 14
```
