# temp stage
FROM python:3.12.2-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

RUN python -m venv /opt/venv
ENV PATH "/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# final stage
FROM python:3.12.2-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH "/opt/venv/bin:$PATH"

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app

# By default, listen on port 5000
EXPOSE 5000/tcp

# Specify the command to run on container start
ENTRYPOINT ["python", "./app.py"]