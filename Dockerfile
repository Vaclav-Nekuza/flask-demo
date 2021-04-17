FROM python:3.8-alpine
EXPOSE 5000
RUN mkdir -p /opt/demo && mkdir -p /etc/demo

WORKDIR /opt/demo

COPY requirements.txt /opt/demo

RUN set -e; \
	apk add --no-cache \
		gcc \
		libc-dev \
		postgresql-dev \
		musl-dev \
		linux-headers \
		bash \
		vim \
		python3-dev \
		libffi-dev \
		build-base \
	; \
	pip install --no-cache-dir -r requirements.txt;

COPY [".", "/opt/demo"]

#CMD ["python", "./run.py"]
ENTRYPOINT ["/usr/local/bin/uwsgi", "--ini", "uwsgi.ini"]
