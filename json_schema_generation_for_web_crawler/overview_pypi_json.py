"""
TODO:
    - [ ] Release Version
        - [ ] Version class with version id as input
        - [ ] develop sorting algorithm for version ids
        - [ ] Version constraint class that takes dependent string as input
        - [ ] Version constraint class that can determine whether a Version obj fit or not
    - [ ] Platform
        - [ ] Develop platform tags data cleaning strategy at PypiVersionPackageVeiw
            - [ ] seperate by ; and ,
            - [ ] lower cases
            - [ ] strip space
            - [ ] allow decomposition into different os
        - [ ] Building Platform node object
    - [ ] Develop python-version property (returning Python-version objs)
    - [ ] Build Dependency-Hyperedge Obj
"""
import typing
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

    @property
    def author_info(self):
        author = self.methods[('info', 'author')]()
        email = self.methods[('info', 'author_email')]()
        return (author, email)

    @property
    def maintainer_info(self):
        maintainer = self.methods[('info', 'maintainer')]()
        email = self.methods[('info', 'maintainer_email')]()
        return (maintainer, email)



class PypiPackageAllVersionView(OverView):
    def __init__(self, pkg):
        self._pkg_view = PyPiPackageView(pkg)
        inputs = [(pkg, version) for version in self.versions]
        super().__init__(PypiVersionPackageView, inputs)

    @property
    def versions(self) -> typing.List[str]:
        """
        Get sorted version ids
        """
        return list(self._pkg_view.released_versions)

    @property
    def releases(self) -> PypiVersionPackageView:
        """
        Get sorted release data objs
        """
        pass

if __name__ == '__main__':
    ver = PypiPackageAllVersionView('pandas').versions[0]
    print(ver)
    p = PypiVersionPackageView('pandas', ver)
    print(p.author_info)
    print(p.maintainer_info)

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
