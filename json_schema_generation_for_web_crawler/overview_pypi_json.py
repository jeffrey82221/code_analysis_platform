from view_json import SingleView, OverView

class PyPiPackageView(SingleView):
    def __init__(self, pkg):
        self._pkg = pkg
        super().__init__(schema=None)
    
    @property
    def url(self):
        return f'https://pypi.org/pypi/{self._pkg}/json'

    @property
    def released_versions(self):
        return set(self.methods[('releases',)]().keys())
    
class PyPiPackageOverView(OverView):
    def __init__(self, pkgs):
        super().__init__(PyPiPackageView, [(p, ) for p in pkgs])
    
    @property
    def released_versions(self):
        result = set()
        for v in self.views:
            try:
                result |= v.released_versions
            except KeyError:
                print('ignore', v._pkg)
        return result

class PypiVersionPackageView(SingleView):
    def __init__(self, pkg, version):
        self._pkg = pkg
        self._version = version
        super().__init__(schema=None)
    @property
    def url(self):
        return f'https://pypi.org/pypi/{self._pkg}/{self._version}/json'


if __name__ == '__main__':
    v = PypiVersionPackageView('pandas', '1.5.0rc0')
    print(v.methods.keys())
    """
    s = PyPiPackageView('pytz')
    print('========================== pandas ================================')
    print(s.methods.keys())
    print(s.methods[('info', 'author')]())
    print(s.released_versions)
    v = PypiVersionPackageView('pandas', '1.5.0rc0')
    print(s.methods.keys())
    print(s.methods[('info', 'requires_dist')]())
    print('done')
    print('========================== overview =============================')
    pkgs = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        for i, pkg in enumerate(f):
            pkg = pkg.strip()
            pkgs.append(pkg)
    o = PyPiPackageOverView(pkgs[:1000])
    print(o.schema)
    print(o.released_versions)
    """