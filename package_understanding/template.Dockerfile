FROM python:3.9
COPY extract_dep_pkgs.py $HOME
RUN ls
RUN python extract_dep_pkgs.py {!python_package!} {!datetime!}