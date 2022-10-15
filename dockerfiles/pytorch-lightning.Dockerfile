FROM python:3.9
COPY extract_dep_pkgs.py $HOME
RUN python extract_dep_pkgs.py pytorch-lightning