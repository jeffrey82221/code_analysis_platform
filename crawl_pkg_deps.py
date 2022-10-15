"""
TODO:
- [ ] Extracting dependency edge list from pypi
    - [X] 1. download package names from pypi: package_names.txt
    - [X] 2. build a new environment of python3.9
    - [X] 3. pip install a package
    - [X] 4. get dependency by checking the folders ("pandas_venv/lib/python3.9/site-packages")
            before and after the package is installed.
    - [ ] 5. allow extract_dep_pkgs to be run in container or colab!
    - [ ] 6. build the dependency edge lists
"""
from main_dep_extraction_api import main as call_deps
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
cnt = sum(1 for line in open('package_names.txt', 'r') if line[0].isalpha())
with ThreadPoolExecutor(max_workers=8) as executor:
    pkg_names = open('package_names.txt')
    gen = filter(lambda x: x[0].isalpha(), pkg_names)
    gen = map(lambda n: n.strip(), gen)
    results_gen = executor.map(call_deps, gen)
    results = list(tqdm(results_gen, total=cnt))
print(len(results))
print(results[0])
