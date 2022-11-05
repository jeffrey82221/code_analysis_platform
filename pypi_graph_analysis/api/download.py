
"""
pip install pypistats
"""
import pypistats
import sys
import json
from httpx import HTTPStatusError
import time

def main(pkg):
    DELAY = 0.01
    cnt_404 = 0
    cnt_429 = 0
    while True:
        try:
            data = json.loads(pypistats.overall(pkg, format="json"))['data']
            result = None
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
                if cnt_429 > 10:
                    print(e.args[0], cnt_429, pkg)
                continue
            elif '404 NOT FOUND' in e.args[0]:
                cnt_404 += 1
                time.sleep(DELAY)
                DELAY += DELAY
                print(e.args[0], cnt_404, pkg)
                if cnt_404 > 10:
                    result = None
                    break
                else:
                    continue
            else:
                raise e
    return result
        

if __name__ == '__main__':
    ans = main(sys.argv[1])
    print(ans)