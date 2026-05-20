FROM python:3.13-alpine AS deps

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Build final image
FROM python:3.13-alpine

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
