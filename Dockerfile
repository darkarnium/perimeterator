FROM python:3.7-stretch

# Define environment varibles used to configure Perimeterator. This is,
# currently, mainly used for documentation purposes.
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG ENUMERATOR_SQS_QUEUE
ARG ENUMERATOR_SQS_REGION
ARG SCANNER_SQS_QUEUE
ARG SCANNER_SQS_REGION

# Install dependencies and setup a home for Perimeterator.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y nmap && \
    useradd -m -d /opt/perimeterator perimeterator

# Install Perimeterator sources into the container.
COPY --chown=perimeterator ./src/ /opt/perimeterator/
COPY --chown=perimeterator ./setup.* /opt/perimeterator/

# Install perimterator.
WORKDIR /opt/perimeterator/
RUN pip3 install . && \
    chown -R perimeterator: /opt/perimeterator

# Kick off the monitor as soon as the container starts (by default).
USER perimeterator
ENTRYPOINT [ "python3", "/opt/perimeterator/scanner.py" ]