# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip --no-cache-dir install --prefix=/install -r requirements.txt

COPY app/ ./app
COPY scripts/ ./scripts
COPY cron/ ./cron

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
ENV TZ=UTC
WORKDIR /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    cron \
    tzdata \
 && rm -rf /var/lib/apt/lists/*

RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

COPY --from=builder /install /usr/local
COPY --from=builder /build/app ./app
COPY --from=builder /build/scripts ./scripts
COPY --from=builder /build/cron ./cron

RUN mkdir -p /data /cron && chmod 755 /data /cron

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

CMD ["/entrypoint.sh"]

# Add this after copying the entrypoint
RUN apt-get update && apt-get install -y dos2unix
RUN dos2unix /entrypoint.sh
RUN chmod +x /entrypoint.sh
