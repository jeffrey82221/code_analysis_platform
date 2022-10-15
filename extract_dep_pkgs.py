
"""
TODO:
- Install package in container 
    - [ ] `docker build -f pkg.Dockerfile -t pkg . --progress=plain`
"""
import subprocess
import os
import sys
import shutil

def main(pkg):
    subprocess.run(f'python -m venv {pkg}_env'.split(), check=True)
    pkg_home = f'./{pkg}_env/lib/python3.9/site-packages'
    try:
        subprocess.run(f'pip install --upgrade pip'.split(), check=True, env=dict(os.environ, PATH=f"{pkg}_env/bin"))
        folder_names_before_install = os.listdir(pkg_home)
        subprocess.run(f'pip install {pkg}'.split(), check=True, env=dict(os.environ, PATH=f"{pkg}_env/bin"))
        folder_names_after_install = os.listdir(pkg_home)
        new_folders = set(folder_names_after_install) - set(folder_names_before_install)
        def is_dist_info(x):
            return x.endswith('.dist-info')
        def convert_py_to_pkg(x):
            if x.endswith('.py'):
                return x.replace('.py', '')
            else:
                return x
        new_pkgs = list(map(convert_py_to_pkg,filter(lambda x: x != '__pycache__' and not is_dist_info(x), 
            list(new_folders))))
        return list(set(new_pkgs) - set([pkg]))
    except BaseException as e:
        import traceback
        print(traceback.format_exc())
        raise e
    finally:
        shutil.rmtree(f'./{pkg}_env')
        
if __name__ == '__main__':
    print('Extract Time:', sys.argv[2])
    deps = main(sys.argv[1])
    print('########## DEPEDENCIES ##########')
    for dep in deps:
        print(f'A-DEP-PACKAGE:\start;{dep}\end;')