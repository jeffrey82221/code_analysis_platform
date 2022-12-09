"""

Overview Graph:
(pkg) <-> (release) -[dep hyper-edge: link-to:{(python_version), (extra), platform}]-> (release: {requires_python, yanked, size}) <-> [(author), (maintainer), (keyword)]

Interesting Raw Feautres:
- author_email :          a related node
- maintainer_email:       a related node
- requires_dist:          a related node (need parsing)
- keywords:               a related node (need parsing)
- project_urls:           a related node (key as property + domain segments as property)
- requires_python:        a node property
- yanked:                 a node property
- releases:               a related node (size, python_version, package_type, upload_time as properties)

Engineered Features:
- number of different project_urls provide:                             node property
- number of version count until the last version:                       node property
- number of different supporting `python_version` over all versions     node property

NOTE:
- get another api result with data specific to a version !
REF: https://discuss.python.org/t/backwards-incompatible-change-to-pypi-json-api/17154
"""
from common.schema_objs import *
Dict({'info': Dict({'author': Optional(Simple(str)),
                    'author_email': Optional(Simple(str)),
                    'bugtrack_url': Simple(None),
                    'classifiers': List(Simple(str)),
                    'description': Simple(str),
                    'description_content_type': Optional(Simple(str)),
                    'docs_url': Optional(Simple(str)),
                    'download_url': Optional(Simple(str)),
                    'downloads': Dict({'last_day': Simple(int),
                                       'last_month': Simple(int),
                                       'last_week': Simple(int)}),
                    'home_page': Optional(Simple(str)),
                    'keywords': Optional(Simple(str)),
                    'license': Optional(Simple(str)),
                    'maintainer': Optional(Simple(str)),
                    'maintainer_email': Optional(Simple(str)),
                    'name': Simple(str),
                    'package_url': Simple(str),
                    'platform': Optional(Simple(str)),
                    'project_url': Simple(str),
                    'project_urls': Optional(DynamicDict({("Homepage",
                                                           260318): Simple(str),
                                                          ("Download",
                                                           67449): Simple(str),
                                                          ("Bug Tracker",
                                                           15039): Simple(str),
                                                          ("Documentation",
                                                           14417): Simple(str),
                                                          ("Repository",
                                                           13514): Simple(str),
                                                          ("Source",
                                                           9592): Simple(str),
                                                          ("Source Code",
                                                           4473): Simple(str),
                                                          ("Tracker",
                                                           2877): Simple(str),
                                                          ("Bug Reports",
                                                           2872): Simple(str),
                                                          ("Changelog",
                                                           2245): Simple(str)})),
                    'release_url': Simple(str),
                    'requires_dist': Optional(List(Simple(str))),
                    'requires_python': Optional(Simple(str)),
                    'summary': Optional(Simple(str)),
                    'version': Simple(str),
                    'yanked': Simple(bool),
                    'yanked_reason': Optional(Simple(str))}),
      'last_serial': Simple(int),
      'releases': UniformDict(List(Dict({'comment_text': Optional(Simple(str)),
                                         'digests': Dict({'md5': Simple(str),
                                                          'sha256': Simple(str)}),
                                         'downloads': Simple(int),
                                         'filename': Simple(str),
                                         'has_sig': Simple(bool),
                                         'md5_digest': Simple(str),
                                         'packagetype': Simple(str),
                                         'python_version': Simple(str),
                                         'requires_python': Optional(Simple(str)),
                                         'size': Simple(int),
                                         'upload_time': Simple(str),
                                         'upload_time_iso_8601': Simple(str),
                                         'url': Simple(str),
                                         'yanked': Simple(bool),
                                         'yanked_reason': Optional(Simple(str))}))),
      'urls': List(Dict({'comment_text': Optional(Simple(str)),
                         'digests': Dict({'md5': Simple(str),
                                          'sha256': Simple(str)}),
                         'downloads': Simple(int),
                         'filename': Simple(str),
                         'has_sig': Simple(bool),
                         'md5_digest': Simple(str),
                         'packagetype': Simple(str),
                         'python_version': Simple(str),
                         'requires_python': Optional(Simple(str)),
                         'size': Simple(int),
                         'upload_time': Simple(str),
                         'upload_time_iso_8601': Simple(str),
                         'url': Simple(str),
                         'yanked': Simple(bool),
                         'yanked_reason': Optional(Simple(str))})),
      'vulnerabilities': List(Dict({'aliases': List(Simple(str)),
                                    'details': Simple(str),
                                    'fixed_in': List(Simple(str)),
                                    'id': Simple(str),
                                    'link': Simple(str),
                                    'source': Simple(str),
                                    'summary': Simple(None),
                                    'withdrawn': Simple(None)}))})
