
"""
pip install pypistats
"""
import pypistats
import sys
import json
from httpx import HTTPStatusError
def main(pkg):
    try:
        data = json.loads(pypistats.overall(pkg, format="json"))['data'][1]
        assert data['category'] == 'without_mirrors'
        return data['downloads']
    except HTTPStatusError:
        print('package not found for', pkg)

if __name__ == '__main__':
    ans = main(sys.argv[1])
    print(ans)