import subprocess
with open('package_names.txt', 'r') as f:
    for line in f:        
        try:
            pkg = line.replace('\n', '')
            print('packge:', pkg)
            subprocess.run(f"python main_dep_extraction.py {pkg}", check=True)
        except:
            print('Install fail on', line) 
            # raise ValueError(f'Install fail on {line}')