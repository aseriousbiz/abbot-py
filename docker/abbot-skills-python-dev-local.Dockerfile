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
ENV SkillApiBaseUriFormatString=http://host.docker.internal:4978/api/skills/{0} \
    AbbotReplyApiUrl=http://host.docker.internal:4978/api/reply \
    AZURE_FUNCTIONS_ENVIRONMENT=Development \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    HTTP_LOGGING_ENABLED=1 \
    AzureWebJobsSecretStorageType=files

EXPOSE 8080
VOLUME ["/azure-functions-host/Secrets"]
COPY ["./src", "/home/site/wwwroot"]
