# Deployment Guide

## Simple Deployment

For development or simple setups, you can run the bot directly:

```bash
python bot.py
```

See the [main README](../README.md) for detailed installation instructions.

## Docker Deployment (Recommended)

For production deployments, we recommend using Docker for better security, isolation, and easier management.

### Quick Start with Docker

1. **Pull the pre-built image:**

   ```bash
   docker pull ghcr.io/wei/thread-it:latest
   ```

2. **Run with environment variables:**
   ```bash
   docker run -d \
     --name thread-it-bot \
     --restart unless-stopped \
     -e DISCORD_TOKEN=your_bot_token_here \
     -e LOG_LEVEL=INFO \
     ghcr.io/wei/thread-it:latest
   ```

### Docker Compose (Recommended)

1. **Create a `.env` file:**

   ```bash
    # Copy the example environment file
    cp .env.example .env

    # Edit .env with your bot token
    # DISCORD_TOKEN=your_bot_token_here
    # LOG_LEVEL=INFO
   ```

2. **Start the bot:**

   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

3. **View logs:**

   ```bash
   docker compose -f docker-compose.prod.yml logs -f thread-it-bot
   ```

4. **Stop the bot:**

   ```bash
   docker compose -f docker-compose.prod.yml down
   ```

5. **Upgrade to latest version:**
   ```bash
   docker compose -f docker-compose.prod.yml pull
   docker compose -f docker-compose.prod.yml up -d
   ```

### Building from Source

```bash
# Build the Docker image
docker build -t thread-it:local .

# Run your local build
docker run -d \
  --name thread-it-bot \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_bot_token_here \
  thread-it:local
```
