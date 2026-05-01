FROM python:3.14-alpine as builder

WORKDIR /build
COPY pyproject.toml src ./
RUN pip install . && rm -R /build

USER 2000:2000
WORKDIR /app
CMD ["rspamd-learn-proxy"]
