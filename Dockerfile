# Stage 1: Install dependencies
FROM python:3-alpine AS deps

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Build final image
FROM python:3-alpine

WORKDIR /app

# ENV DISCORD_TOKEN=
# ENV LOG_LEVEL=INFO

COPY --from=deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY *.py .

CMD ["python", "bot.py"]
