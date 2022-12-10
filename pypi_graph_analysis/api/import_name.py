
"""
Get the import name of a package
"""
import os
import glob
import sys
import traceback
DELETE = True


def main(pkg):
    try:
        os.mkdir(f'pkg/{pkg}')
        os.mkdir(f'pkg/{pkg}_unpacked')
        os.system(f'pip download {pkg} --no-deps --dest pkg/{pkg}')
        os.system(f'wheel unpack pkg/{pkg}/*.whl -d pkg/{pkg}_unpacked')
        file_name = glob.glob(
            f'pkg/{pkg}_unpacked/*/*.dist-info/top_level.txt')[0]
        import_name = open(file_name, 'r').read().strip()
        if '\n' in import_name:
            import_name = import_name.split('\n')[0]
    except BaseException as e:
        print(traceback.format_exc())
        print(f'Package {pkg} not found')
        import_name = None
    finally:
        if DELETE:
            if os.path.exists(f'pkg/{pkg}'):
                os.system(f'rm -r pkg/{pkg}')
            if os.path.exists(f'pkg/{pkg}_unpacked'):
                os.system(f'rm -r pkg/{pkg}_unpacked')
        print('import_name:', import_name)
        return import_name


if __name__ == '__main__':
    ans = main(sys.argv[1])
    print(ans)
