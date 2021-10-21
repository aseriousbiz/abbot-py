FROM abbotacr02.azurecr.io/abbot-skills-python:latest

# development environment
ENV AbbotApiBaseUrl=http://host.docker.internal:4978/api \
    AZURE_FUNCTIONS_ENVIRONMENT=Development \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    HTTP_LOGGING_ENABLED=1 \
    AzureWebJobsSecretStorageType=files

EXPOSE 8080
VOLUME ["/azure-functions-host/Secrets"]
