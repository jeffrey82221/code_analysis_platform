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
import requests
from bs4 import BeautifulSoup

pypi_index = 'https://pypi.python.org/simple/'
print(f'GET list of packages from {pypi_index}')
try:
    resp = requests.get(pypi_index, timeout=5)
except requests.exceptions.RequestException:
    print('ERROR: Could not GET the pypi index. Check your internet connection.')
    exit(1)

print(f'NOW parsing the HTML (this could take a couple of seconds...)')
try:
    soup = BeautifulSoup(resp.text, 'html.parser')
    body = soup.find('body')
    links = (pkg for pkg in body.find_all('a'))
    pkg_names = [link['href'].split('/')[-2] for link in list(links)]
except:
    print('ERROR: Could not parse pypi HTML.')
    exit(1)

with open('package_names.txt', 'w') as f:
    for n in pkg_names:
        f.write(n+'\n')

