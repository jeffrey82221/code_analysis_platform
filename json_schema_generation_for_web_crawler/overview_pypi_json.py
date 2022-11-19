"""
TODO:
    - [X] Release Version
        - [X] Version class with version id as input
        - [X] develop sorting algorithm for version ids
        - [X] parsing of required_dist str
        - [X] Version constraint class that takes dependent string as input
        - [X] Version constraint class that can determine whether a Version obj fit or not
        - [X] Ignoring RC versions
    - [ ] Platform
        - [ ] Develop platform tags data cleaning strategy at PypiVersionPackageVeiw
            - [X] seperate by ; and ,
            - [X] lower cases
            - [X] strip space
            - [ ] allow decomposition into different os
        - [ ] Building Platform node object
    - [ ] Develop python-version property (returning Python-version objs)
        - [X] Search for all python versions
        - [X] Version constraint class that takes dependent string as input
        - [X] Version constraint class that can determine whether a Version obj fit or not
        - [ ] Embedding into the Big class
    - [ ] Build Dependency-Hyperedge Obj
"""
import copy
import re
import requests
from bs4 import BeautifulSoup
import typing
from concurrent.futures import ThreadPoolExecutor
from common.view_json import SingleView, OverView


class Version:
    def __init__(self, ver_id: str):
        self._ver_id = ver_id
        self._id = [int(i) for i in ver_id.split('.')]

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, x):
        return self._id == x._id

    def __ge__(self, x):
        return self._id >= x._id

    def __gt__(self, x):
        return self._id > x._id

    def __le__(self, x):
        return self._id <= x._id

    def __lt__(self, x):
        return self._id < x._id

    def __repr__(self):
        return f'Version[{self._ver_id}]'


class PythonVersion(Version):
    def __repr__(self):
        return f'PythonVersion[{self._ver_id}]'

    def __hash__(self):
        return hash(str(self._ver_id))


def python_versions():
    text = requests.get('https://www.python.org/downloads/source/').text
    soup = BeautifulSoup(text, 'html.parser')
    gen = filter(lambda x: 'Python-' in x,
                 [l.get('href') for l in soup.findAll('a')])
    gen = map(lambda x: x.split('/python/')[1].split('/Python-')[0], gen)
    return sorted(list(set(map(lambda x: PythonVersion(x), gen))))


PY_VERS = python_versions()


class SimpleConstraint:
    def __init__(self, contraint_str):
        contraint_str = contraint_str.strip()
        if '>=' in contraint_str:
            self._mode = '>='
            self._ver = contraint_str.split('>=')[1]
        elif '>' in contraint_str:
            self._mode = '>'
            self._ver = contraint_str.split('>')[1]
        elif '<=' in contraint_str:
            self._mode = '<='
            self._ver = contraint_str.split('<=')[1]
        elif '<' in contraint_str:
            self._mode = '<'
            self._ver = contraint_str.split('<')[1]
        elif '==' in contraint_str:
            self._mode = '=='
            self._ver = contraint_str.split('==')[1]
        elif '!=' in contraint_str:
            self._mode = '!='
            self._ver = contraint_str.split('!=')[1]
        elif '~=' in contraint_str:
            self._mode = '~='
            self._ver = contraint_str.split('~=')[1]
        else:
            self._mode = ''
            self._ver = None

    def __repr__(self):
        return f'S[{self._mode}{self._ver}]'

    def fit(self, version: Version) -> bool:
        if self._mode == '':
            return True
        code = f'version {self._mode} Version("{self._ver}")'
        ans = eval(code)
        return ans

    def filter(
            self, versions: typing.Iterable[Version]) -> typing.Iterable[Version]:
        return filter(lambda v: self.fit(v), versions)


class Constraint:
    def __init__(self, contraint_str: str):
        contraint_str = contraint_str.strip()
        if ',' in contraint_str:
            self._constraints = [SimpleConstraint(
                c) for c in contraint_str.split(',')]
        else:
            self._constraints = [SimpleConstraint(contraint_str)]

    def fit(self, version: Version) -> bool:
        return all([c.fit(version) for c in self._constraints])

    def filter(
            self, versions: typing.Iterable[Version]) -> typing.Iterable[Version]:
        return filter(lambda v: self.fit(v), versions)

    def __repr__(self):
        str_ = ','.join(map(str, self._constraints))
        return f'C[{str_}]'


class PyPiPackageView(SingleView):
    def __init__(self, pkg):
        self._pkg = pkg
        super().__init__(schema=None)

    @property
    def url(self):
        return f'https://pypi.org/pypi/{self._pkg}/json'

    @property
    def released_versions(self):
        vs = []
        for id in self.methods[('releases',)]().keys():
            try:
                vs.append(Version(id))
            except ValueError:
                pass
        return sorted(vs)


class PypiVersionPackageView(SingleView):
    def __init__(self, pkg, version):
        self._pkg = pkg
        self._version = version
        super().__init__(schema=None)

    def __repr__(self):
        return f'Package[{self._pkg}=={self._version}]'

    @property
    def url(self):
        return f'https://pypi.org/pypi/{self._pkg}/{self._version}/json'

    @property
    def author_info(
            self) -> typing.Tuple[typing.Optional[str], typing.Optional[str]]:
        author = self.methods[('info', 'author')]()
        email = self.methods[('info', 'author_email')]()
        if author == '':
            author = None
        if email == '':
            email = None
        return (author, email)

    @property
    def maintainer_info(
            self) -> typing.Tuple[typing.Optional[str], typing.Optional[str]]:
        maintainer = self.methods[('info', 'maintainer')]()
        email = self.methods[('info', 'maintainer_email')]()
        if maintainer == '':
            maintainer = None
        if email == '':
            email = None
        return (maintainer, email)

    @property
    def requires_dist(self):
        result = []
        for con_str in self.methods[('info', 'requires_dist')]():
            result.append(DepConstraint(con_str))
        return result

    @property
    def requires_python(self) -> typing.List[PythonVersion]:
        constraint_str = self.methods[('info', 'requires_python')]()
        constraint = Constraint(constraint_str)
        return sorted(list(filter(constraint.fit, PY_VERS)))

    @property
    def platform(self):
        platform_str = self.methods[('info', 'platform')]()
        if isinstance(platform_str, str):
            if ',' in platform_str:
                platforms = [x.lower().strip()
                             for x in platform_str.split(',')]
            elif ';' in platform_str:
                platforms = [x.lower().strip()
                             for x in platform_str.split(';')]
            else:
                platforms = [platform_str.lower().strip()]
            return platforms
        else:
            return platform_str

    @property
    def summary(self):
        return self.methods[('info', 'summary')]()


class PypiPackageAllVersionView(OverView):
    def __init__(self, pkg):
        self._pkg = pkg
        self._pkg_view = PyPiPackageView(pkg)
        inputs = [(pkg, version._ver_id) for version in self.versions]
        super().__init__(PypiVersionPackageView, inputs)

    @property
    def versions(self) -> typing.List[Version]:
        """
        Get sorted version ids
        """
        return self._pkg_view.released_versions

    @property
    def releases(self) -> PypiVersionPackageView:
        """
        Get sorted release data objs
        """
        def get_result(v):
            return PypiVersionPackageView(self._pkg, v._ver_id)

        with ThreadPoolExecutor(max_workers=8) as executor:
            return list(executor.map(get_result, self.versions, chunksize=2))


class DepConstraint:
    """
    Hyperedge linked to
    1. [X] package
    2. [X] releases
    3. condition
        3.1. platform
        3.2. python version
        3.3. underlie package
        3.4. non-package extra
    """

    def __init__(self, dep_constraint_str):
        """
        Input example:
        pytest (>=7.1.2,<8.0.0); (python_full_version > "3.6.0") and (extra == "test")

        ~=0.6 means >=0.6, ==0.*
        """
        if ';' in dep_constraint_str:
            dep_str, condition_str = dep_constraint_str.split(';')
        else:
            dep_str = dep_constraint_str.strip()
            condition_str = ''
        if '(' in dep_str and ')' in dep_str:
            self._pkg = dep_str.split(' (')[0].strip()
            ver_constraint_str = dep_str.split('(')[1].split(')')[0].strip()
            self._ver_constraint = Constraint(ver_constraint_str)
        else:
            self._pkg = re.split(f'[<|>|=|!|~]', dep_str)[0].strip()
            self._ver_constraint = Constraint(dep_str.split(self._pkg)[1])
        self._condition_str = condition_str.strip()

    def __repr__(self):
        return f'D[{self._pkg}@Ver[{self._ver_constraint}]@Cond[{self._condition_str}]]'

    @property
    def depend_releases(self):
        """
        Get sorted release data objs
        """
        def get_result(v):
            return PypiVersionPackageView(self._pkg, v._ver_id)

        with ThreadPoolExecutor(max_workers=4) as executor:
            return list(executor.map(
                get_result, self._depend_versions, chunksize=1))

    @property
    def _depend_versions(self):
        versions = self._depend_package.versions
        return sorted(filter(self._ver_constraint.fit, versions))

    @property
    def _depend_package(self):
        return PypiPackageAllVersionView(self._pkg)


if __name__ == '__main__':
    releases = PypiPackageAllVersionView('pandas').releases
    for dist in releases[-1].requires_dist:
        print(dist)
        print(dist.depend_releases)
    """
    print(releases)
    print(releases[-1])
    print(releases[-1].requires_python)
    print(releases[-1].requires_dist)
    dep = releases[-1].requires_dist[0]
    print(dep)
    dependent_releases = PypiPackageAllVersionView(dep._pkg).releases
    print(dependent_releases)
    print(DepConstraint('alabaster>=0.7,<0.8'))

    p = releases[-1]
    print(p.author_info)
    print(p.maintainer_info)
    print(p.requires_python)
    print(p.platform)
    print(python_versions())
    """
    """
    print('========================== overview =============================')

    pkgs = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        for i, pkg in enumerate(f):
            pkg = pkg.strip()
            pkgs.append(pkg)
    o = PyPiPackageOverView(pkgs[:1000])

    with open('platform.txt', 'w') as f:
        for re_py in o.get('info', 'platform'):
            if re_py is not None:
                f.write(re_py.strip()+'\n')


    import json
    with open('released_versions.json', 'w') as f:
        json.dump(o.released_versions, f)


    with open('requires_dist.txt', 'w') as f:
        for re_dis in o.get('info', 'requires_dist', '_list_'):
            if re_dis is not None:
                f.write(re_dis + '\n')

    """
