ARG BUILD_BRANCH=""
ARG BUILD_SHA=""
ARG PYTHON_VERSION="3.9"
FROM python:${PYTHON_VERSION}-buster

# Upgrade any OS packages with outstanding upgrades, to ensure we've got security fixes.
RUN apt-get --allow-releaseinfo-change update && apt-get upgrade -qyy && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY ./src/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Bring the rest of the app in
COPY ./src /app

RUN echo "${BUILD_BRANCH}\n${BUILD_SHA}" > "/app/build_info.txt"
ENV AbbotApiBaseUrl=https://app.ab.bot/api
ENV HOST="0.0.0.0"
ENV PORT="80"
ENV ABBOT_SANDBOX_POLICY="permissive"
ENTRYPOINT [ "python3", "/app/runner.py" ]