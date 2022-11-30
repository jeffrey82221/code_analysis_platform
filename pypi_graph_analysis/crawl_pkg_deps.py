"""
Step 2: crawl dependent package of all packages of pypi
Input: package_names.txt
Output: deps/<pkg_name>.json
"""
from api.dep import main as call_deps
from concurrent.futures import ThreadPoolExecutor
import json
import os
from tqdm import tqdm
import io
cnt = sum(1 for line in open('package_names.txt', 'r') if line[0].isalpha())


def call_n_save_result(pkg):
    path = f'deps/{pkg}.json'
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                deps = json.load(f)
        except io.UnsupportedOperation as e:
            raise e
    else:
        deps = call_deps(pkg)
        with open(path, 'w') as f:
            json.dump(deps, f)
    return deps


def consumer(gen):
    for i, result in enumerate(tqdm(gen, total=cnt)):
        if i % 10000 == 0:
            print(f'{i}th result:', result)


with ThreadPoolExecutor(max_workers=8) as executor:
    pkg_names = open('package_names.txt')
    gen = filter(lambda x: x[0].isalpha(), pkg_names)
    gen = map(lambda n: n.strip(), gen)
    results_gen = executor.map(call_n_save_result, gen)
    consumer(results_gen)
