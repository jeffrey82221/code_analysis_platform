"""
Package Node
"""
from common.view_json import SingleView
from .version import Version

__all__ = ['Package']


class Package(SingleView):
    def __init__(self, pkg, schema=None):
        self._pkg = pkg
        super().__init__(schema=schema)

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
