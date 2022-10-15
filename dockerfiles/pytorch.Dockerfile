FROM python:3.9
COPY extract_dep_pkgs.py $HOME
RUN ls
RUN python extract_dep_pkgs.py pytorch 2022-10-15T20:40:31.520167