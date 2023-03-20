ARG BUILD_BRANCH=""
ARG BUILD_SHA=""
ARG PYTHON_VERSION="3.9"
FROM python:${PYTHON_VERSION}-buster

# Install dependencies
COPY ./src/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Bring the rest of the app in
COPY ./src /app

RUN echo "${BUILD_BRANCH}\n${BUILD_SHA}" > "/app/build_info.txt"
ENV AbbotApiBaseUrl=https://app.ab.bot/api

ENTRYPOINT [ "python3", "/app/runner.py" ]