# Thread It - Discord Bot Design Specification

Version: 1.0

Date: June 23, 2025

## 1\. Introduction & Vision

"Thread It" is a utility bot for Discord servers designed to promote organized and contextual conversations. The primary goal is to automatically convert message replies into public threads. By doing so, it keeps main channel feeds clean and ensures that follow-up discussions are neatly contained, preventing conversations from cluttering the primary channel view. The bot aims to be seamless and operate in the background, gently guiding users towards using threads for collaborative discussions without requiring manual commands.

## 2\. Core Functionality

The bot's logic is centered around a single, critical event: a user replying to a message in a channel.

### 2.1. Event Trigger: Message Creation

- **Event Listener:** The bot will listen to the `messageCreate` event across all channels it has access to on a server.

- **Initial Checks:**

  - The bot will ignore messages sent by other bots (including itself) to prevent loops.

  - The bot will ignore messages that are not replies (`message.reference` is null).

  - The bot will ignore messages that are already inside a thread.

### 2.2. Reply-to-Thread Conversion Logic

When a valid reply message is detected, the following sequence of actions will be executed:

1.  **Identify Reply:** The bot confirms that the new message is a direct reply to another message in the channel.

2.  **Gather Information:** The bot will cache the following information from the reply message:

    - The content of the reply message.

    - The author of the reply message.

    - Any attachments (files) or embeds on the message.

    - The channel where the reply was sent.

    - The original message that was replied to (the "parent" message).

3.  **Create a Public Thread:** The bot will create a new public thread on the parent message.

    - **Thread Name:** The thread's name will be automatically generated.

    - **Auto-Archive Duration:** A default duration of 24 hours of inactivity will be set.

4.  **Re-post the Reply in the Thread:** The bot will post the content of the deleted reply into the newly created thread.

    - **Attribution:** The message will be formatted to clearly indicate the original author. A common practice is using a webhook or an embed to post the message under the original user's name and avatar. For v1.0, a simple text-based attribution is sufficient:

      > **Reply from @[Original Author]:**
      >
      > [Original message content]

    - **Attachments & Embeds:** Any files or embeds from the user's original reply will be included in the message posted by the bot.

5.  **Delete System Message:** The bot will identify and delete the automatic Discord message that says `"[Bot Name] started a thread"`. This ensures the process is as unobtrusive as possible.

6.  **Delete the Original Reply:** After the thread is created and the content has been successfully reposted, the bot will delete the user's original reply message from the main channel. A `try/catch` block will be essential here to handle potential permission errors gracefully.

### 2.3. Desired User Experience Flow

1.  **User A** posts a message in `#general`.

2.  **User B** uses the "Reply" function to post a message directed at User A, possibly with an attached image.

3.  **Instantly**, User B's reply message disappears from `#general`.

4.  A new thread appears on User A's message.

5.  Inside the new thread, a message appears containing the content of User B's reply (and the image), attributed to User B.

6.  The main `#general` channel remains clean, with only a "View Thread" button on User A's message.

## 3\. Technical Specification

- **Language:** Python

- **Primary Library:** discord.py

- **Documentation:** [discord.py documentation](https://context7.com/rapptz/discord.py/llms.txt)

## 4\. Discord Bot Configuration

### 4.1. Bot Permissions (Gateway Intents)

The bot will require the following permissions to be granted during the OAuth2 URL generation:

| Permission                   | Reason                                                           |
| ---------------------------- | ---------------------------------------------------------------- |
| **View Channels**            | To see messages in channels.                                     |
| **Send Messages**            | To send the reply content into the new thread.                   |
| **Send Messages in Threads** | To send the reply content into the new thread.                   |
| **Create Public Threads**    | The core functionality of the bot.                               |
| **Manage Messages**          | To delete the original user reply and the system message.        |
| **Read Message History**     | To fetch the content of the message being replied to, if needed. |

### 4.2. Gateway Intents

The bot will require the following Gateway Intents to be enabled in the Discord Developer Portal:

| Intent            | Reason                                                                                                                                                   |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GUILDS`          | Standard intent for server-related events.                                                                                                               |
| `GUILD_MESSAGES`  | To receive message creation events.                                                                                                                      |
| `MESSAGE_CONTENT` | **(Privileged Intent)** Required to read the content of messages. This must be explicitly enabled in the bot's settings on the Discord Developer Portal. |

## 5\. Error Handling & Edge Cases

- **Missing Permissions:** If the bot fails to delete a message or create a thread, it should log the error with the server ID and channel ID. It should not crash. The operation for that specific reply will be aborted.

- **API Errors:** All interactions with the Discord API (deleting messages, creating threads, sending messages) will be wrapped in `try/catch` blocks.

- **Replying to a Bot:** The bot will ignore all messages from any bot, including itself, to prevent recursive loops.

- **Message Content Too Long for Thread Title:** Thread titles have a character limit (100). The bot will truncate any generated title to fit within this limit.

## 6\. Deployment & Setup Guide

1.  **Create Bot Application:** Go to the Discord Developer Portal, create a new application, and add a Bot user.

2.  **Enable Intents:** Enable the Privileged Gateway Intents as specified in section 4.2.

3.  **Get Bot Token:** Copy the bot's token. This will be used as an environment variable (`DISCORD_TOKEN`).

4.  **Invite Bot:** Generate an OAuth2 URL with the permissions outlined in section 4.1 and invite the bot to the desired server(s).

5.  **Run the Bot.**
