# Thread It - Discord Bot Design Specification

Version: 1.0

Date: June 24, 2025

## 1\. Introduction & Vision

"Thread It" is a utility bot for Discord servers designed to promote organized and contextual conversations. The primary goal is to automatically convert message replies into public threads. By doing so, it keeps main channel feeds clean and ensures that follow-up discussions are neatly contained, preventing conversations from cluttering the primary channel view. The bot aims to be seamless and operate in the background, gently guiding users towards using threads for collaborative discussions without requiring manual commands.

## 2\. Core Functionality

The bot's logic is centered around a single, critical event: a user replying to a message in a channel.

### 2.1. Event Trigger: Message Creation

- **Event Listener:** The bot listens to the `on_message` event across all channels it has access to on a server.

- **Initial Validation Checks:**

  - The bot ignores messages sent by bots (including itself) to prevent loops.

  - The bot ignores messages that are not replies (`message.reference` is null).

  - The bot ignores messages that are already inside a thread.

  - The bot only processes messages in guild channels (not DMs).

### 2.2. Reply-to-Thread Conversion Logic

When a valid reply message is detected, the following sequence of actions is executed:

1.  **Additional Validation:** The bot performs additional edge case checks:

    - Validates the parent message still exists and is accessible
    - Confirms the message is in a valid guild
    - Checks if the channel supports thread creation
    - Validates bot permissions before proceeding

2.  **Gather Information:** The bot caches the following information from the reply message:

    - The content of the reply message
    - The author of the reply message
    - Any attachments (files) or embeds on the message
    - The channel where the reply was sent
    - The original message that was replied to (the "parent" message)
    - Message ID and creation timestamp

3.  **Create a Public Thread:** The bot creates a new public thread on the parent message:

    - **Thread Name:** Automatically generated from parent message content using smart truncation
    - **Auto-Archive Duration:** 24 hours (1440 minutes) of inactivity
    - **Thread Type:** Public thread attached to the parent message

4.  **Re-post the Reply in the Thread:** The bot posts the content of the reply into the newly created thread:

    - **Attribution:** Uses a Discord embed with the author's avatar, display name, and timestamp for rich visual attribution
    - **Content Preservation:** Maintains all original text content within the embed description
    - **Attachments:** Downloads and re-uploads all file attachments
    - **Embeds:** Preserves all embed content from the original reply alongside the new attribution embed
    - **Thread Participation:** Automatically adds the original reply author as a participant in the thread

5.  **Clean Up Messages:** The bot performs cleanup operations:
    - **Delete Original Reply:** Removes the user's original reply message from the main channel
    - **Send Temporary Notification:** Sends a brief message directing the user to continue in the thread, which auto-deletes after 8 seconds
    - **Delete System Messages:** Automatically detects and removes Discord's system thread creation messages

### 2.3. Desired User Experience Flow

1.  **User A** posts a message in `#general`.

2.  **User B** uses the "Reply" function to post a message directed at User A, possibly with an attached image.

3.  **Instantly**, User B's reply message disappears from `#general`.

4.  A new thread appears on User A's message with an intelligently generated name.

5.  Inside the new thread, a message appears containing the content of User B's reply (and the image), attributed to User B.

6.  The main `#general` channel remains clean, with only a "View Thread" button on User A's message.

## 3\. Technical Specification

### 3.1. Implementation Details

- **Language:** Python 3.9+
- **Primary Library:** discord.py (>=2.3.0)
- **Dependencies:** python-dotenv (>=1.0.0)
- **Architecture:** Single-file bot with modular configuration
- **Configuration:** Environment variable-based with `.env` file support

### 3.2. Core Classes and Components

#### ThreadItBot Class

- **Base Class:** `discord.Client`
- **Key Methods:**
  - `on_message()`: Main event handler for processing message replies
  - `process_reply_to_thread()`: Orchestrates the reply-to-thread conversion
  - `gather_reply_information()`: Extracts and validates reply data
  - `create_thread_from_reply()`: Creates threads with intelligent naming
  - `repost_reply_in_thread()`: Reposts content with attribution
  - `cleanup_messages()`: Handles message deletion and cleanup
  - `validate_permissions()`: Checks bot permissions before operations

#### Config Class

- **Purpose:** Centralized configuration management
- **Key Features:**
  - Environment variable integration
  - Thread naming logic with smart truncation
  - Configurable auto-archive duration (24 hours default)
  - Discord API limits enforcement (100 character thread names)

### 3.3. Thread Naming Algorithm

The bot implements intelligent thread naming:

1. Extracts content from the parent message
2. Removes Discord mentions, links, and formatting
3. Cleans whitespace and newlines
4. Truncates to 100 characters (Discord limit) with ellipsis
5. Falls back to "Discussion Thread" for empty content

## 4\. Discord Bot Configuration

### 4.1. Required Bot Permissions

The bot requires the following permissions to be granted during OAuth2 URL generation:

| Permission                   | Reason                                                           |
| ---------------------------- | ---------------------------------------------------------------- |
| **View Channels**            | To see messages in channels.                                     |
| **Send Messages**            | To send the reply content into the new thread.                   |
| **Send Messages in Threads** | To send the reply content into the new thread.                   |
| **Create Public Threads**    | The core functionality of the bot.                               |
| **Manage Messages**          | To delete the original user reply and the system message.        |
| **Read Message History**     | To fetch the content of the message being replied to, if needed. |

### 4.2. Required Gateway Intents

The bot requires the following Gateway Intents to be enabled in the Discord Developer Portal:

| Intent            | Reason                                                                                                                                                   |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GUILDS`          | Standard intent for server-related events.                                                                                                               |
| `GUILD_MESSAGES`  | To receive message creation events.                                                                                                                      |
| `MESSAGE_CONTENT` | **(Privileged Intent)** Required to read the content of messages. This must be explicitly enabled in the bot's settings on the Discord Developer Portal. |

## 5\. Error Handling & Edge Cases

### 5.1. Comprehensive Error Handling

The bot implements robust error handling throughout all operations:

- **Permission Validation:** Pre-validates all required permissions before attempting operations
- **API Error Handling:** All Discord API interactions are wrapped in try/catch blocks
- **Graceful Degradation:** Operations fail gracefully without crashing the bot
- **Detailed Logging:** Comprehensive logging for monitoring and debugging

### 5.2. Specific Edge Cases

- **Missing Permissions:** Bot validates permissions and logs detailed error messages with server/channel context
- **Parent Message Not Found:** Handles cases where the replied-to message has been deleted
- **Rate Limiting:** Implements rate limit handling with a simple backoff (defaults to a 5 second wait)
- **Attachment Processing:** Gracefully handles attachment download/upload failures
- **Thread Creation Failures:** Handles Discord API errors during thread creation
- **Message Deletion Failures:** Continues operation even if cleanup fails

### 5.3. Bot Behavior Rules

- **Bot Message Filtering:** Ignores all messages from bots to prevent recursive loops
- **Thread Name Truncation:** Automatically truncates thread names to Discord's 100-character limit
- **DM Filtering:** Only processes messages in guild channels, ignores direct messages
- **Thread Channel Filtering:** Ignores messages already posted in threads

## 6\. Configuration & Environment

### 6.1. Environment Variables

| Variable        | Required | Default | Description                                           |
| --------------- | -------- | ------- | ----------------------------------------------------- |
| `DISCORD_TOKEN` | ✅       | None    | Discord bot token from Developer Portal               |
| `LOG_LEVEL`     | ❌       | INFO    | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

### 6.2. Configuration Constants

- **Auto-Archive Duration:** 1440 minutes (24 hours)
- **Max Thread Name Length:** 100 characters (Discord limit)
- **Default Thread Name:** "Discussion Thread" (fallback)

## 7\. Logging & Monitoring

### 7.1. Logging Features

- **Console-Only Logging:** Simplified logging without file rotation or complex file management
- **Structured Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Operation Metrics:** Performance tracking with duration measurements
- **Discord.py Noise Reduction:** Discord library logging set to WARNING level

### 7.2. Log Categories

- **Bot Lifecycle:** Startup, guild join/leave events, connection status
- **Operation Tracking:** Reply processing, thread creation, message cleanup
- **Error Reporting:** Permission issues, API failures, unexpected errors
- **Performance Metrics:** Operation duration and success/failure rates

## 8\. Deployment & Setup Guide

### 8.1. Prerequisites

- Python 3.9 or higher
- Discord bot token from Discord Developer Portal
- Server with appropriate permissions

### 8.2. Installation Steps

1.  **Create Bot Application:** Go to the Discord Developer Portal, create a new application, and add a Bot user.

2.  **Enable Intents:** Enable the Privileged Gateway Intents as specified in section 4.2.

3.  **Get Bot Token:** Copy the bot's token for use as the `DISCORD_TOKEN` environment variable.

4.  **Clone Repository:** Download or clone the Thread It bot code.

5.  **Install Dependencies:** Run `pip install -r requirements.txt` to install discord.py and python-dotenv.

6.  **Configure Environment:** Create a `.env` file with your `DISCORD_TOKEN` and optional `LOG_LEVEL`.

7.  **Invite Bot:** Generate an OAuth2 URL with the permissions outlined in section 4.1 and invite the bot to the desired server(s).

8.  **Run the Bot:** Execute `python bot.py` to start the bot.

### 8.3. Bot Status

The bot sets its Discord status to "Watching for replies to convert to threads" to indicate its active monitoring state.
