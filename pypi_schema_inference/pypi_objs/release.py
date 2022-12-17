"""
Package Node
"""

import typing
from concurrent.futures import ThreadPoolExecutor
from common.view_json import SingleView, OverView
from .version import Version, PythonVersion, Constraint
from .package import Package


__all__ = ['Release', 'Releases']


class Release(SingleView):
    def __init__(self, pkg, version, schema=None):
        self._pkg = pkg
        self._version = version
        self._schema = schema
        super().__init__(schema=schema)

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
    """
    @property
    def requires_dist(self):
        from .dependency import Dependency
        result = []
        for con_str in self.methods[('info', 'requires_dist')]():
            result.append(Dependency(con_str))
        return result
    """
    @property
    def requires_dist(self):
        from .dependency import Dependency

        def get_result(con_str):
            dep = Dependency(con_str, schema=self._schema)
            return dep, dep.depend_releases
        dep_constraints = self.methods[('info', 'requires_dist')]()
        with ThreadPoolExecutor(max_workers=len(dep_constraints)) as executor:
            result = list(
                executor.map(
                    get_result,
                    dep_constraints,
                    chunksize=1))
        return dict(result)

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


class Releases(OverView):
    def __init__(self, pkg, schema=None):
        self._pkg = pkg
        self._pkg_view = Package(pkg, schema=schema)
        inputs = [(pkg, version._ver_id) for version in self.versions]
        self._schema = schema
        super().__init__(Release, inputs, schema=schema)

    @property
    def versions(self) -> typing.List[Version]:
        """
        Get sorted version ids
        """
        return self._pkg_view.released_versions

    @property
    def releases(self) -> typing.List[Release]:
        """
        Get sorted release data objs
        """
        def get_result(v):
            return Release(self._pkg, v._ver_id, schema=self._schema)

        with ThreadPoolExecutor(max_workers=len(self.versions)) as executor:
            return list(executor.map(get_result, self.versions, chunksize=1))
