FROM mcr.microsoft.com/azure-functions/python:3.0-python3.7-buildenv as build
WORKDIR output
COPY src/ .
RUN pip install --target=./ -r ./requirements.txt

FROM mcr.microsoft.com/azure-functions/python:3.0-python3.7-slim

# required container environment
ENV \
    # Enable detection of running in a container
    DOTNET_RUNNING_IN_CONTAINER=true \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 \
    DOTNET_NOLOGO=true \
    FUNCTIONS_EXTENSION_VERSION=~3 \
    ASPNETCORE_URLS=http://+:8080

# development environment
ENV AbbotApiBaseUrl=http://host.docker.internal:4978/api \
    AZURE_FUNCTIONS_ENVIRONMENT=Development \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    HTTP_LOGGING_ENABLED=1 \
    AzureWebJobsSecretStorageType=files

EXPOSE 8080
VOLUME ["/azure-functions-host/Secrets"]
COPY --from=build ["./output", "/home/site/wwwroot"]
