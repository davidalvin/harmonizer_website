FROM tiangolo/uwsgi-nginx-flask:python3.7-2020-12-19
WORKDIR /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

# Install muscore
RUN echo "deb http://deb.debian.org/debian buster-backports main" > /etc/apt/sources.list.d/custom.list && \
    apt-get update && \
    apt-get -y -t buster-backports install "musescore3"

ADD . /app
# run the command to start uWSGI
CMD ["uwsgi", "uwsgi.ini"]
