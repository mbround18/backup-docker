FROM python:3.12-slim as base

# Install cron and Pipenv
RUN apt-get update && apt-get install -y cron procps && pip install pipenv

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and Pipfile(s) to the container
COPY . /app

# Install dependencies using Pipenv
RUN pipenv --python /usr/local/bin/python3 install --deploy --ignore-pipfile

# Use the official Python base image
FROM base as script

# Define the SCHEDULE environment variable (default is every minute as an example)
ENV INPUT_FOLDER="/app/input"
ENV OUTPUT_FOLDER="/app/output"
ENV SCHEDULE="0 * * * *"

# Use the startup script as the entry point
ENTRYPOINT ["python"]
CMD ["main.py"]

FROM script as cron

WORKDIR /app

# Copy the cron file to the cron.d directory
COPY ./scripts /app/scripts

# Give execution rights on the cron job
RUN chmod +x /app/scripts/*

# Apply cron job
ENTRYPOINT ["bash"]
CMD ["/app/scripts/entrypoint.sh"]

