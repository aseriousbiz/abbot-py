FROM mcr.microsoft.com/azure-functions/python:3.0-python3.9-buildenv as build

# Upgrade any OS packages with outstanding upgrades, to ensure we've got security fixes.
RUN apt-get update && apt-get upgrade -qyy && rm -rf /var/lib/apt/lists/*

WORKDIR output
COPY src/requirements.txt .
RUN pip install --target=./ -r ./requirements.txt
COPY src/ .

FROM mcr.microsoft.com/azure-functions/python:3.0-python3.7-slim

# Upgrade any OS packages with outstanding upgrades, to ensure we've got security fixes.
RUN apt-get update && apt-get upgrade -qyy && rm -rf /var/lib/apt/lists/*

ENV \
    # Enable detection of running in a container
    DOTNET_RUNNING_IN_CONTAINER=true \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 \
    DOTNET_NOLOGO=true \
    FUNCTIONS_EXTENSION_VERSION=~3 \
    ASPNETCORE_URLS=http://+:8080 \
    AbbotApiBaseUrl=https://ab.bot/api

EXPOSE 8080
COPY --from=build ["./output", "/home/site/wwwroot"]
