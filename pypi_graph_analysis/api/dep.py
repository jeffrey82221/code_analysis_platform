
"""
Check Dependency Via PyPi API
"""
import requests
import sys
import os


def parse_result(dep):
    if "extra == 'test'" in dep:
        mode = 'test-dep'
    else:
        mode = 'dep'
    if '(' in dep and ')' in dep:
        result = dep.split(' (')[0]
    else:
        result = dep.split(';')[0]
    if '[' in result and ']' in result:
        result = result.split('[')[0]
    return (result.strip(), mode)


def main(pkg, verbose=False):
    url = f'https://pypi.org/pypi/{pkg}/json'
    json = requests.get(url).json()
    if 'info' in json:
        if verbose and 'project_urls' in json['info'] and json['info']['project_urls'] is not None:
            if 'Source Code' in json['info']['project_urls']:
                print(json['info']['project_urls']['Source Code'])
            elif 'Download' in json['info']['project_urls']:
                print(json['info']['project_urls']['Download'])
        if json['info']['requires_dist'] is not None:
            result = list(map(parse_result, json['info']['requires_dist']))
        else:
            result = []
        if verbose:
            print('dep found for', pkg)
        return [list(x) for x in list(set(result))]
    else:
        if verbose:
            print('package not found for', pkg)


if __name__ == '__main__':
    try:
        verbose = (sys.argv[2] == '1')
    except:
        verbose = False
    print('verbose:', verbose)
    deps = main(sys.argv[1], verbose=verbose)
    if verbose and isinstance(deps, list):
        print(deps)
        for dep in deps:
            if dep[1] == 'dep':
                print('#', dep[0])
                os.system(f'python pkg_desc_api.py {dep[0]}')
