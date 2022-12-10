
"""
pip install pypistats
"""
from redis_decorators import RedisCaching
import time
from httpx import HTTPStatusError
import json
import pypistats
import sys
"""
pip install redis-decorators
pip install fakeredis
"""
caching = RedisCaching('redis://localhost:6379')
# Define a custom `CacheElement`


@caching.cache_string()
def call_pypistats(pkg):
    DELAY = 0.01
    cnt_404 = 0
    cnt_429 = 0
    while True:
        try:
            result = -1
            data = json.loads(pypistats.overall(pkg, format="json"))['data']
            if len(data) == 2:
                if data[1]['category'] == 'without_mirrors':
                    result = data[1]['downloads']
                elif data[0]['category'] == 'with_mirrors':
                    result = data[0]['downloads']
            if len(data) == 1:
                if data[0]['category'] == 'without_mirrors':
                    result = data[0]['downloads']
            time.sleep(DELAY)
            break
        except KeyError as e:
            print('key error on', data)
            raise e
        except HTTPStatusError as e:
            if '429 TOO MANY REQUESTS' in e.args[0]:
                cnt_429 += 1
                time.sleep(DELAY)
                DELAY += DELAY
                if cnt_429 > 8:
                    print(e.args[0], cnt_429, pkg)
                continue
            elif '404 NOT FOUND' in e.args[0]:
                cnt_404 += 1
                time.sleep(DELAY)
                DELAY += DELAY
                print(e.args[0], cnt_404, pkg)
                if cnt_404 > 6:
                    break
                else:
                    continue
            else:
                raise e
    return result


def main(pkg):
    result = call_pypistats(pkg)
    if isinstance(result, str):
        result = int(result)
    return result


if __name__ == '__main__':
    ans = main(sys.argv[1])
    print(ans)
