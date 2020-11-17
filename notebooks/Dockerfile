FROM jupyter/base-notebook

ADD ./ /home/jovyan/work

USER root
WORKDIR /home/jovyan/work/utils
RUN python setup.py install
#error: could not create 'utils.egg-info': Permission denied
#https://github.com/jupyter/docker-stacks/issues/408

USER jovyan
WORKDIR /home/jovyan/work
RUN conda install --quiet --yes 'pandas' --channel conda-forge

WORKDIR /home/jovyan/work
RUN pip install --no-cache-dir -r requirements.txt

