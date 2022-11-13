"""

Overview Graph: 
(pkg) <-> (release) -> (release: {requires_python, yanked}) <-> [(author), (maintainer), (keyword)] 

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
from schema_objs import *
Dict[{
    'info': Dict[{
        'author': Optional[str], # Author Node Name 
        'author_email': Optional[str], # Author Node Property
        'bugtrack_url': None,
        'classifiers': List[str], # Simple Property: List of description tags (need formating)
        'description': str,  # Simple Property: List of description (need formating)
        'description_content_type': Optional[str], # Simple Property: type of descyption
        'docs_url': Optional[str], # Mostly None 
        'download_url': Optional[str], # Need truncate to the domain name (avoid UNKNOWN and '')
        'downloads': Dict[{'last_day': int, 'last_month': int, 'last_week': int}], # Many -1
        'home_page': Optional[str],
        'keywords': Optional[str], # Need seperate by ','
        'license': Optional[str],
        'maintainer': Optional[str],
        'maintainer_email': Optional[str],
        'name': str,
        'package_url': str,
        'platform': Optional[str],
        'project_url': str,
        'project_urls': Optional[DynamicDict[{
            'Changelog': str, 'Issue tracker': str, 'Viessmann': str, 'Changes': str, 'Issue Tracker': str, 'Issues': str, 'documentation': str, 'homepage': str, 'Article': str, 'repository': str, 'Repository': str, 'Bug Tracker': str, 'Homepage': str, 'Source': str, 'Issue / Bug Reports': str, 'Download': str, 'Documentation': str, 'changelog': str, 'GitHub': str, 'G002 Recommendation': str, 'Source Code': str, 'Tracker': str, 'PyPI': str, 'Online Interpreter': str, 'Git Repository': str, 'Home': str, 'Twitter': str, 'Funding': str, 'PyPI Releases': str, 'ABC Dataset': str, 'Bug Reports': str, 'Release Notes': str, 'Binder': str, 'Release Management': str
        }]],
        'release_url': str,
        'requires_dist': Optional[List[str]],
        'requires_python': Optional[str],
        'summary': str,
        'version': str, # this is the last release version 
        'yanked': bool,
        'yanked_reason': None
    }],
    'last_serial': int,
    'releases': UniformDict[List[Dict[{
        'comment_text': Optional[str],
        'digests': Dict[{'md5': str, 'sha256': str}],
        'downloads': int,
        'filename': str,
        'has_sig': bool,
        'md5_digest': str,
        'packagetype': str,
        'python_version': str,
        'requires_python': Optional[str],
        'size': int,
        'upload_time': str,
        'upload_time_iso_8601': str,
        'url': str,
        'yanked': bool,
        'yanked_reason': Optional[str]
    }]]],
    'urls': List[Dict[{ # urls only contain data of the latest version
        'comment_text': Optional[str],
        'digests': Dict[{'md5': str, 'sha256': str}],
        'downloads': int,
        'filename': str,
        'has_sig': bool,
        'md5_digest': str,
        'packagetype': str,
        'python_version': str,
        'requires_python': Optional[str],
        'size': int,
        'upload_time': str,
        'upload_time_iso_8601': str,
        'url': str,
        'yanked': bool,
        'yanked_reason': None
    }]],
    'vulnerabilities': List[?]
}]
