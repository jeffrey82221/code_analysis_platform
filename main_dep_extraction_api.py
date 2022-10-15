
"""
TODO:
- Install package in container
    - [ ] `docker build -f pkg.Dockerfile -t pkg . --progress=plain`
"""
import requests
import sys

VERBOSE = False


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
    return result.strip(), mode


def main(pkg):
    url = f'https://pypi.org/pypi/{pkg}/json'
    json = requests.get(url).json()
    if 'info' in json:
        if VERBOSE and 'project_urls' in json['info'] and json['info']['project_urls'] is not None:
            if 'Source Code' in json['info']['project_urls']:
                print(json['info']['project_urls']['Source Code'])
            elif 'Download' in json['info']['project_urls']:
                print(json['info']['project_urls']['Download'])
        if json['info']['requires_dist'] is not None:
            result = list(map(parse_result, json['info']['requires_dist']))
        else:
            result = []
        if VERBOSE:
            print('dep found for', pkg)
        return result
    else:
        if VERBOSE:
            print('package not found for', pkg)


if __name__ == '__main__':
    deps = main(sys.argv[1])
    print(deps)
