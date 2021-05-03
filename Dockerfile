FROM nvcr.io/nvidia/tensorflow:21.04-tf2-py3
WORKDIR /tmp
ENV PYTHONPATH=/tmp
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r requirements.txt
