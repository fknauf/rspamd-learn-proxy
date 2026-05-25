FROM python:3.14-alpine AS builder

WORKDIR /build
COPY pyproject.toml src ./
RUN pip install . && rm -R /build

USER 2000:2000
WORKDIR /app
CMD ["rspamd-learn-proxy"]

HEALTHCHECK \
  --interval=5m \
  --timeout=5s \
  --retries=3 \
  --start-period=5s \
  CMD netstat -tln | egrep ":(${HAM_PORT:-9000}|${SPAM_PORT:-9001})"
