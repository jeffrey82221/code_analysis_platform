# General

- [ ] organize the folder (sort by analysis topics)

# Inter-package analyzer 

Build graph of depedency between packages for analysis

- [X] Crawl data from pypi API 
- [X] Build Dependency Graph on RedisGraph
- [ ] Get package real import name via:

```python
import importlib_metadata
importlib_metadata.packages_distributions()
```

- [X] Cypher-analysis DEMO notes
      - [ ] Way of adding PageRank score back to graph as node property
      - [ ] Way determining edges weights (define by number of import / number of function call / number of class inheritance / etc.) 
      - [ ] Way of propagating population degrees (such as Star count, fork count) to all nodes-based on edge weights
      - [ ] Way of applying PageRank-like algorithm on heterogeneous graph
- [ ] Add additional node properties
      - [ ] github link
      - [ ] github Star Count 
      - [ ] `Indended Audience` on PyPi
      - [ ] package description
      - [ ] download per month (ref: https://pepy.tech/project)
      - [ ] slope of max per-day download count against version update
- [ ] Add additional relationships
      - [ ] package-to-forking Github account 

# Intra-package analyzer

Build graph of dependency between class/func/package/etc within a package

- [ ] Download github repo of package on PyPi
- [ ] Load package into RedisGraph via pycograph
- [ ] Cypher-analysis DEMO notes
    - [ ] Identify external pacakges 

# Non-graph code analyzing tools:

- [ ] A README.md containing all debugging tools found.
- [ ] A folder containing demo code of each debugging tools.

 
