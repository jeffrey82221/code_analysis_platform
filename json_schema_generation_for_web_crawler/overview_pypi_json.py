from common.view_json import SingleView, OverView

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
        result = dict()
        for v in self.views:
            try:
                result[v._pkg] = sorted(v.released_versions)
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
    
    """
    v = PypiVersionPackageView('pandas', '1.5.0rc0')
    print(v.methods.keys())
    s = PyPiPackageView('pytz')
    print('========================== pandas ================================')
    print(s.methods.keys())
    print(s.methods[('info', 'author')]())
    print(s.released_versions)
    v = PypiVersionPackageView('pandas', '1.5.0rc0')
    print(s.methods.keys())
    print(s.methods[('info', 'requires_dist')]())
    print('done')
    
    """

    print('========================== overview =============================')
    
    pkgs = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        for i, pkg in enumerate(f):
            pkg = pkg.strip()
            pkgs.append(pkg)
    o = PyPiPackageOverView(pkgs[:10000])
    
    print(o.method_keys)
    with open('requires_python.txt', 'w') as f:
        for re_py in o.get('info', 'requires_python'):
            if re_py is not None:
                f.write(re_py.strip()+'\n')
    import json
    with open('released_versions.json', 'w') as f:
        json.dump(o.released_versions, f)
    
    
    with open('requires_dist.txt', 'w') as f:
        for re_dis in o.get('info', 'requires_dist', '_list_'):
            if re_dis is not None:
                f.write(re_dis + '\n')
