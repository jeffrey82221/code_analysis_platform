from modulefinder import ModuleFinder
import glob
import os
pkg = 'pandas'
pkg_path = glob.glob(f'{pkg}*/{pkg}')[0]
deps = []
for root, dirs, files in os.walk(f'./{pkg_path}'):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            with open(file_path, "r") as fp:
                for line in [l.strip() for l in fp if 'import ' in l]:
                    try:
                        if line.startswith('from'):
                            dep = line.split(' ')[1]
                            deps.append(dep)
                        elif line.startswith('import'):
                            dep = line.split(' ')[1]
                            deps.append(dep)
                    except BaseException as e:
                        print(line)
                        raise e

cleaned_deps = []
for dep in set(deps):
    if dep.startswith('.'):
        dep = dep[1:]
    if '.' in dep:
        cleaned_deps.append(dep.split('.')[0])
    else:
        cleaned_deps.append(dep)

deps = sorted(list(set(cleaned_deps) - set([pkg])))
print(deps)
