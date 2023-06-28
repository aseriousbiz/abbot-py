FROM mcr.microsoft.com/azure-functions/python:4-python3.9-buildenv as build
ARG BUILD_BRANCH=""
ARG BUILD_SHA=""

# Remove jessie from sources.list, it's EOL
RUN sed -i '/jessie/d' /etc/apt/sources.list

# Upgrade any OS packages with outstanding upgrades, to ensure we've got security fixes.
RUN apt-get --allow-releaseinfo-change update && apt-get upgrade -qyy && rm -rf /var/lib/apt/lists/*

WORKDIR output
COPY src/requirements.txt .
RUN pip install --target=./ -r ./requirements.txt
COPY src/ .
RUN echo "${BUILD_BRANCH}\n${BUILD_SHA}" > "/output/build_info.txt"

FROM mcr.microsoft.com/azure-functions/python:4-python3.9-slim

# Remove jessie from sources.list, it's EOL
RUN sed -i '/jessie/d' /etc/apt/sources.list

# Upgrade any OS packages with outstanding upgrades, to ensure we've got security fixes.
RUN apt-get --allow-releaseinfo-change update && apt-get upgrade -qyy && rm -rf /var/lib/apt/lists/*

# Remove jessie from sources.list, it's EOL
RUN sed -i '/jessie/d' /etc/apt/sources.list

# Run a pip upgrade of a few packages in the "root" Python environment to make the scanner happier
RUN pip install --upgrade pip setuptools wheel

ENV \
    # Enable detection of running in a container
    DOTNET_RUNNING_IN_CONTAINER=true \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 \
    DOTNET_NOLOGO=true \
    FUNCTIONS_EXTENSION_VERSION=~3 \
    ASPNETCORE_URLS=http://+:8080 \
    AbbotApiBaseUrl=https://app.ab.bot/api

EXPOSE 8080
COPY --from=build ./output /home/site/wwwroot
