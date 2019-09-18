# OS
FROM surnet/alpine-python-wkhtmltopdf:3.7.3-0.12.5-full
LABEL maintainer='dev@agilize.com.br'

# packages
RUN apk add --no-cache \
	bash

# python installs
RUN pip install \
	werkzeug \
	executor \
	gunicorn

# set working dir
# WORKDIR /root

# copy app
COPY app.py .

# port expose
EXPOSE 80

# entry point
ENTRYPOINT ["/usr/local/bin/gunicorn"]

# run app
CMD ["-b", "0.0.0.0:80", "--log-file", "-", "app:application"]