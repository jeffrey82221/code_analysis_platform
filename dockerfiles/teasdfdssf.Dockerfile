FROM python:3.9
COPY extract_dep_pkgs.py $HOME
RUN ls
RUN python extract_dep_pkgs.py teasdfdssf 2022-10-15T21:16:36.655674