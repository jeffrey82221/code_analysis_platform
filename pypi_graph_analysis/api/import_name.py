
"""
Get the import name of a package 
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