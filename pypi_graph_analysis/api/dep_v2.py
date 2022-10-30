
"""
Get the import dependency of a package 

pip install pycograph

pycograph load --project-dir networkx/networkx-2.8.7/networkx/ --graph-name networkx --redis-port 9001
pycograph load --project-dir torch_unpacked/torch-1.13.0/torch/ --graph-name torch --redis-port 9001


pip download pandas --dest pandas
pip download torch --dest torch
"""
import os
import glob
import sys
def main(pkg):
    try:
        os.system(f'mkdir {pkg}')
        os.system(f'mkdir {pkg}_unpacked')
        os.system(f'pip download {pkg} --no-deps --dest {pkg}')
        os.system(f'wheel unpack {pkg}/*.whl -d {pkg}_unpacked')
        file_name = glob.glob(f'{pkg}_unpacked/*/*.dist-info/top_level.txt')[0]
        import_name = open(file_name, 'r').read().strip()
        return import_name
    except:
        print(f'Package {pkg} not found')
    finally:
        if os.path.exists(pkg):
            os.system(f'rm -r {pkg}')
        if os.path.exists(f'{pkg}_unpacked'):
            os.system(f'rm -r {pkg}_unpacked')
    
if __name__ == '__main__':
    ans = main(sys.argv[1])
    print(ans)