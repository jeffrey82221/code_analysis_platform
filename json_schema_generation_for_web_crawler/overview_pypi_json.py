"""
TODO:
    - [ ] Release Version
        - [X] Version class with version id as input
        - [X] develop sorting algorithm for version ids
        - [ ] Version constraint class that takes dependent string as input
        - [ ] Version constraint class that can determine whether a Version obj fit or not
    - [ ] Platform
        - [ ] Develop platform tags data cleaning strategy at PypiVersionPackageVeiw
            - [X] seperate by ; and ,
            - [X] lower cases
            - [X] strip space
            - [ ] allow decomposition into different os
        - [ ] Building Platform node object
    - [ ] Develop python-version property (returning Python-version objs)
        - [ ] Search for all python versions
    - [ ] Build Dependency-Hyperedge Obj
"""
import typing
from common.view_json import SingleView, OverView

class Version:
    def __init__(self, ver_id: str):
        self._ver_id = ver_id
        self._id = [str(i) if i.isdigit() else i for i in ver_id.split('.')]

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, x):
        return self._id == x._id

    def __ge__(self, x):
        return self._id > x._id

    def __lt__(self, x):
        try:
            return self._id < x._id
        except BaseException as e:
            print('self._id', self._id, 'x._id', x._id)
            raise e

    def __repr__(self):
        return f'Version[{self._ver_id}]'

class PyPiPackageView(SingleView):
    def __init__(self, pkg):
        self._pkg = pkg
        super().__init__(schema=None)
    
    @property
    def url(self):
        return f'https://pypi.org/pypi/{self._pkg}/json'

    @property
    def released_versions(self):
        return sorted([Version(id) for id in self.methods[('releases',)]().keys() if 'rc' not in id])
    
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

    @property
    def requires_python(self):
        return self.methods[('info', 'requires_python')]()


    @property
    def platform(self):
        platform_str = self.methods[('info', 'platform')]()
        if isinstance(platform_str, str):
            if ',' in platform_str:
                platforms = [x.lower().strip() for x in platform_str.split(',')]
            elif ';' in platform_str:
                platforms = [x.lower().strip() for x in platform_str.split(';')]
            else:
                platforms = [platform_str.lower().strip()]
            return platforms
        else:
            return platform_str

class PypiPackageAllVersionView(OverView):
    def __init__(self, pkg):
        self._pkg = pkg
        self._pkg_view = PyPiPackageView(pkg)
        inputs = [(pkg, version._ver_id) for version in self.versions]
        super().__init__(PypiVersionPackageView, inputs)

    @property
    def versions(self) -> typing.List[str]:
        """
        Get sorted version ids
        """
        return self._pkg_view.released_versions

    @property
    def releases(self) -> PypiVersionPackageView:
        """
        Get sorted release data objs
        """
        return [PypiVersionPackageView(self._pkg, v._ver_id) for v in self.versions]


if __name__ == '__main__':
    releases = PypiPackageAllVersionView('tensorflow').releases
    print(releases)
    p = releases[-1]
    print(p.author_info)
    print(p.maintainer_info)
    print(p.requires_python)
    print(p.platform)
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
