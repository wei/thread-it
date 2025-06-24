![Thread It 🧵](https://socialify.git.ci/wei/thread-it/image?custom_language=Discord&description=1&font=Rokkitt&language=1&logo=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2Fsvgmoji%2Fsvgmoji%2F%2Fpackages%2Fsvgmoji__blob%2Fsvg%2F1F9F5.svg&name=1&owner=1&pattern=Circuit+Board&theme=Light)

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Discord bot that automatically keeps channels clean by converting message replies into organized public threads. Thread It promotes organized conversations by seamlessly moving reply discussions into dedicated threads, preventing channel clutter while maintaining context.

## 📋 Table of Contents

- [Features](#-features)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Required Permissions](#-required-permissions)
- [Support & Documentation](#-support--documentation)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **Automatic Thread Creation**: Converts message replies into organized public threads
- **Clean Channel Management**: Keeps main channels clutter-free by moving discussions to threads
- **Smart Thread Naming**: Automatically generates meaningful thread names from original message content
- **Seamless Operation**: Works in the background without requiring manual commands
- **Content Preservation**: Maintains all reply content including text, attachments, and embeds
- **Permission Validation**: Ensures proper bot permissions before attempting operations
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Error Handling**: Robust error handling with graceful fallbacks

## 🔄 How It Works

1. **User posts a message** in a Discord channel
2. **Another user replies** to that message
3. **Thread It detects the reply** and automatically:
   - Creates a public thread on the original message
   - Moves the reply content into the new thread
   - Removes the original reply from the main channel
   - Preserves all attachments, embeds, and formatting

The result: Clean main channels with organized discussions in dedicated threads!

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- A Discord bot token
- Discord server with appropriate permissions

### Step 1: Clone the Repository

```bash
git clone https://github.com/wei/thread-it.git
cd thread-it
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Navigate to the "Bot" section
4. Create a bot and copy the token
5. Enable the following **Privileged Gateway Intents**:
   - Message Content Intent (required)
6. Generate an invite URL with these **permissions**:
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Create Public Threads
   - Manage Messages
   - Read Message History

### Step 5: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your bot token
# DISCORD_TOKEN=your_bot_token_here
# LOG_LEVEL=INFO
```

### Step 6: Run the Bot

```bash
python bot.py
```

## ⚙️ Configuration

Thread It uses environment variables for configuration. Create a `.env` file in the project root:

```env
# Required: Your Discord bot token
DISCORD_TOKEN=your_bot_token_here

# Optional: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

### Configuration Options

| Variable        | Required | Default | Description             |
| --------------- | -------- | ------- | ----------------------- |
| `DISCORD_TOKEN` | ✅       | None    | Your Discord bot token  |
| `LOG_LEVEL`     | ❌       | INFO    | Logging verbosity level |

### Thread Settings

The bot includes several configurable settings in `config.py`:

- **Auto-archive Duration**: Threads auto-archive after 24 hours (1440 minutes)
- **Thread Name Length**: Maximum 100 characters (Discord limit)
- **Thread Naming**: Automatically generated from original message content

> **Note**: Based on previous discussions, rate limiting and file logging parameters have been simplified. The bot now uses streamlined logging without complex file rotation or rate limiting configurations.

## 📖 Usage

Once installed and running, Thread It works automatically! No commands are needed.

### Example Workflow

```
Main Channel:
👤 Alice: "What's everyone's favorite Python library?"

👤 Bob: "I love requests for HTTP calls!" (replies to Alice's message)
```

**Result**: Thread It automatically creates a thread titled "What's everyone's favorite Python library?" and moves Bob's reply into it.

### Supported Content Types

- ✅ Text messages
- ✅ Images and attachments
- ✅ Embeds
- ✅ Message formatting (bold, italic, code blocks, etc.)
- ✅ Mentions and links (cleaned from thread names)

### Bot Behavior

- **Ignores bot messages**: Prevents infinite loops
- **Only processes replies**: Regular messages are left untouched
- **Skips existing threads**: Won't create threads within threads
- **Validates permissions**: Checks required permissions before acting
- **Handles errors gracefully**: Logs issues without crashing

## 🔐 Required Permissions

Thread It requires specific Discord permissions to function properly. When inviting the bot to your server, ensure these permissions are granted:

### Bot Permissions

| Permission               | Purpose                            |
| ------------------------ | ---------------------------------- |
| View Channels            | Read messages in channels          |
| Send Messages            | Send messages in main channels     |
| Send Messages in Threads | Send messages in created threads   |
| Create Public Threads    | Create threads on messages         |
| Manage Messages          | Delete original reply messages     |
| Read Message History     | Access message history for context |

### Gateway Intents

The following intents must be enabled in the Discord Developer Portal:

- **Message Content Intent** (Privileged): Required to read message content

### Permission Issues?

If you're experiencing permission-related problems, see our [Troubleshooting Guide](docs/TROUBLESHOOTING.md#permission-errors) for detailed solutions.

## 📞 Support & Documentation

### Getting Help

- **🐛 Issues**: [Report bugs or request features](https://github.com/wei/thread-it/issues)
- **🔧 Troubleshooting**: [Common issues and solutions](docs/TROUBLESHOOTING.md)
- **📖 Design Docs**: [Technical specification](docs/design-specification.md)
- **📚 Discord.py**: [Official discord.py documentation](https://discordpy.readthedocs.io/)

### Quick Links

- **Having problems?** → Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- **Want to contribute?** → See the [Contributing Guide](docs/CONTRIBUTING.md)
- **Need API details?** → View the [Contributing Guide](docs/CONTRIBUTING.md#api-documentation)

## 🤝 Contributing

We welcome contributions to Thread It! Whether you want to fix bugs, add features, or improve documentation, your help is appreciated.

**Quick Start for Contributors:**

1. Read the [Contributing Guide](docs/CONTRIBUTING.md)
2. Fork the repository
3. Set up your development environment
4. Make your changes
5. Submit a pull request

For detailed development setup, code style guidelines, testing requirements, and submission process, see our comprehensive [Contributing Guide](docs/CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Summary**: You can use, modify, and distribute this project freely for commercial or private use. No warranty is provided.

---

## 🙏 Acknowledgments

- **Discord.py** - The excellent Python library for Discord bot development
- **Discord** - For providing the platform and API
- **Contributors** - Everyone who has contributed to making Thread It better
- **Community** - Users who provide feedback and report issues

---

<div align="center">

**Made with ❤️ by [@wei](https://github.com/wei)**

[⭐ Star this repo](https://github.com/wei/thread-it) | [🐛 Report Bug](https://github.com/wei/thread-it/issues) | [💡 Request Feature](https://github.com/wei/thread-it/issues)

</div>
