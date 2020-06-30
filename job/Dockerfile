FROM python:3

# copy our application code
ADD ./job /opt/job
ADD ./utils /opt/job/utils
ADD ./experiments/prediction.py /opt/job/experiments/prediction.py

# set a directory for the app & install dependencies
WORKDIR /opt/job
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py install