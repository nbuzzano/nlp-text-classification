FROM python:3

# copy our application code
ADD ./flask-app /opt/flask-app
ADD ./utils /opt/flask-app/utils

# set a directory for the app & install dependencies
WORKDIR /opt/flask-app
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py install