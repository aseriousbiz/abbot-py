FROM mcr.microsoft.com/azure-functions/python:4-python3.7-buildenv as build
WORKDIR output
COPY src/requirements.txt .
RUN pip install --target=./ -r ./requirements.txt
COPY src/ .
FROM scratch AS export-stage
COPY --from=build ["./output", "."]
