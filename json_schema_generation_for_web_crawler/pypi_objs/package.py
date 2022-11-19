"""
Package Node
"""

import typing
from common.view_json import SingleView
from .version import Version, PythonVersion, Constraint
from .dependency import Dependency


__all__ = ['Package', 'Release', 'Releases']


class Package(SingleView):
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

class Release(SingleView):
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
            result.append(Dependency(con_str))
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
