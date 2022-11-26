"""
Dependency Hyperedge Node
"""
import re
import typing
from concurrent.futures import ThreadPoolExecutor
from .version import Version, Constraint
from .release import Release, Releases


class Dependency:
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

    def __init__(self, dep_constraint_str, schema=None):
        """
        Input example:
        pytest (>=7.1.2,<8.0.0); (python_full_version > "3.6.0") and (extra == "test")

        ~=0.6 means >=0.6, ==0.*
        """
        self._schema = schema
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
            self._pkg = re.split(r'[<|>|=|!|~]', dep_str)[0].strip()
            self._ver_constraint = Constraint(dep_str.split(self._pkg)[1])
        self._condition_str = condition_str.strip()

    def __repr__(self):
        return f'D[{self._pkg}@Ver[{self._ver_constraint}]@Cond[{self._condition_str}]]'

    @property
    def depend_releases(self) -> typing.List[Release]:
        """
        Get sorted release data objs
        """
        def get_result(v):
            return Release(self._pkg, v._ver_id, schema=self._schema)

        with ThreadPoolExecutor(max_workers=len(self._depend_versions)) as executor:
            return list(executor.map(
                get_result, self._depend_versions, chunksize=1))

    @property
    def _depend_versions(self) -> typing.List[Version]:
        versions = self._depend_package.versions
        return sorted(filter(self._ver_constraint.fit, versions))

    @property
    def _depend_package(self) -> Releases:
        return Releases(self._pkg, schema=self._schema)
