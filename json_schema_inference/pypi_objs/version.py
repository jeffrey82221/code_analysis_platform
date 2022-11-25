"""
Version and Constraint ORMs
"""
import typing
import requests
from bs4 import BeautifulSoup


__all__ = ['Version', 'PythonVersion', 'PY_VERS', 'Constraint']

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
