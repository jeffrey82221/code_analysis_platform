FROM python:3.9
COPY extract_dep_pkgs.py $HOME
RUN ls
RUN python extract_dep_pkgs.py torch 2022-10-15T21:13:40.492811