import os
import sys
import subprocess
from datetime import datetime
import shutil


def parse_log(path):
    match = False
    with open(path, 'r') as f:
        for line in f:
            if '########## DEPEDENCIES ##########' in line:
                match = True
            if match and 'A-DEP-PACKAGE:\\start;' in line:
                yield line.split('A-DEP-PACKAGE:\\start;')[1].split('\\end;')[0]


def main(pkg):
    log_path = f'build_logs/{pkg}.log'
    if os.path.exists(log_path):
        return list(parse_log(log_path))
    else:
        with open('template.Dockerfile', 'r') as f:
            dockerfile = f.read().replace(
                '{!python_package!}', pkg).replace(
                '{!datetime!}', str(
                    datetime.now()).replace(
                    ' ', 'T'))
        with open(f'dockerfiles/{pkg}.Dockerfile', 'w') as f:
            f.write(dockerfile)
        try:
            os.system(
                f'docker build -f dockerfiles/{pkg}.Dockerfile -t {pkg} . &> build_logs/{pkg}.log')
            image_id = os.popen(
                f"docker images -q '{pkg}' | uniq").readlines()[0].replace('\n', '')
            subprocess.run(
                f"docker rmi --force".split() +
                [image_id],
                check=True)
            subprocess.run(f"docker image prune --force".split(), check=True)
            return list(parse_log(log_path))
        except BaseException as e:
            if os.path.exists(log_path):
                os.remove(log_path)
            raise ValueError('Failed installing the package') from e
        finally:
            os.remove(f'dockerfiles/{pkg}.Dockerfile')


if __name__ == '__main__':
    ans = main(sys.argv[1])
    print('DEP:', ans)
