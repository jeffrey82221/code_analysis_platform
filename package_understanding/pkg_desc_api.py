
"""
Package Discription Crawled from PyPi
"""
import requests
import sys

VERBOSE = True


def main(pkg):
    url = f'https://pypi.org/pypi/{pkg}/json'
    json = requests.get(url).json()
    if 'info' in json:
        result = json['info']['summary']
        return result
    else:
        if VERBOSE:
            print('package not found for', pkg)


if __name__ == '__main__':
    pkg = sys.argv[1]
    desc = main(pkg)
    print(f"Summary of {pkg}:\n\n", desc, '\n\n')
