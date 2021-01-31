FROM python:3.6

#INSTALL requirements.txt
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY ./src /opt/webapp/src

WORKDIR /opt/webapp

CMD ["python", "src/app.py"]