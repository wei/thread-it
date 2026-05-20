# Pinned to a specific digest so rebuilds are reproducible and cannot be
# silently shifted by an upstream tag move. Bump deliberately via PR.
FROM python:3.13.13-alpine3.23@sha256:420cd0bf0f3998275875e02ecd5808168cf0843cbb4d3c536432f729247b2acc AS deps

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Build final image
FROM python:3.13.13-alpine3.23@sha256:420cd0bf0f3998275875e02ecd5808168cf0843cbb4d3c536432f729247b2acc

WORKDIR /app

# ENV DISCORD_TOKEN=
# ENV LOG_LEVEL=INFO

COPY --from=deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY *.py .

# Drop root: create an unprivileged user and own /app.
RUN addgroup -S threadit && adduser -S -G threadit threadit \
    && chown -R threadit:threadit /app

USER threadit

CMD ["python", "bot.py"]
