FROM debian:latest

WORKDIR /collector
ENV VIRTUAL_ENV="$WORKDIR/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update \
	&& apt-get install -y \
	python3 python3-venv python3-pip \
	&& apt-get clean

#ENV HTTP_PROXY="http://###"
#ENV HTTPS_PROXY="http://###"
#ENV no_proxy=grafana

# Copy application
RUN mkdir config
RUN mkdir functions
RUN mkdir functions_core
RUN mkdir install
RUN mkdir keys
#RUN mkdir tests

ADD config config
ADD functions functions
ADD functions_core functions_core
ADD install install
ADD keys keys
ADD logs logs
#ADD tests tests
ADD main.py .

#RUN python3 -m pip install --upgrade pip
RUN python3 -m venv $VIRTUAL_ENV
RUN . $VIRTUAL_ENV/bin/activate

# Install dependencies:
ADD install/requirements.txt install
RUN pip3 install -r install/requirements.txt


# Run the application:
CMD ["python3", "main.py"]
