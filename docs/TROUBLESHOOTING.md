# Troubleshooting Thread It 🔧

This guide helps you diagnose and resolve common issues with the Thread It Discord bot.

## 📋 Table of Contents

- [Common Issues](#-common-issues)
- [Debug Mode](#-debug-mode)
- [Performance Considerations](#-performance-considerations)
- [Getting Help](#-getting-help)
- [Log Analysis](#-log-analysis)

## 🚨 Common Issues

### Bot Not Responding

**Problem**: Bot is online but not creating threads from replies.

**Symptoms**:

- Bot shows as online in Discord
- Replies are posted but no threads are created
- No error messages in console output

**Solutions**:

1. **Check Permissions**: Ensure the bot has all required permissions in the channel

   ```
   Required permissions:
   ✅ View Channels
   ✅ Send Messages
   ✅ Send Messages in Threads
   ✅ Create Public Threads
   ✅ Manage Messages
   ✅ Read Message History
   ```

2. **Verify Intents**: Confirm Message Content Intent is enabled in Discord Developer Portal

   - Go to Discord Developer Portal → Your Application → Bot
   - Enable "Message Content Intent" under Privileged Gateway Intents

3. **Check Console Output**: Look for error messages in the console where the bot is running

   ```bash
   # Enable debug logging for more detailed output
   LOG_LEVEL=DEBUG
   ```

4. **Test in Different Channel**: Try in a channel where you know permissions are correct

### Permission Errors

**Problem**: Bot logs permission-related errors.

**Common Error Messages**:

```
Missing permission 'Create Public Threads' in channel #general
Bot lacks required permissions: ['Manage Messages', 'Send Messages in Threads']
```

**Solutions**:

1. **Re-invite Bot**: Generate a new invite URL with updated permissions

   - Use the Discord Developer Portal to generate a new OAuth2 URL
   - Include all required permissions listed above

2. **Check Channel Overrides**: Verify channel-specific permissions don't block the bot

   - Right-click channel → Edit Channel → Permissions
   - Check if bot role has necessary permissions

3. **Role Hierarchy**: Ensure bot's role is high enough in the server hierarchy
   - Server Settings → Roles
   - Move bot role higher if needed

### Thread Creation Fails

**Problem**: Bot attempts to create threads but fails.

**Error Messages**:

```
Failed to create thread: 403 Forbidden
Thread creation failed: Missing Access
```

**Solutions**:

1. **Server Boost Level**: Some servers require boosts for certain thread features

   - Check if your server has the required boost level for threads
   - Some thread features require Server Boost Level 2

2. **Channel Type**: Ensure the channel supports threads (text channels only)

   - Threads can only be created in text channels
   - Voice channels and other channel types don't support threads

3. **Rate Limits**: Check if hitting Discord API rate limits
   - Monitor console output for rate limit messages
   - Consider implementing delays if processing high volumes

### Bot Crashes or Stops

**Problem**: Bot goes offline unexpectedly.

**Common Causes**:

- Invalid or regenerated Discord token
- Network connectivity issues
- Memory or resource constraints
- Unhandled exceptions

**Solutions**:

1. **Check Token**: Verify Discord token is valid and not regenerated

   ```bash
   # Test token validity
   DISCORD_TOKEN=your_token_here python bot.py
   ```

2. **Review Console Output**: Look for error messages in the console before the crash

   - Check the terminal/console where you're running the bot
   - Look for error messages, stack traces, or warnings
   - Note any patterns or specific error codes

3. **Memory Usage**: Monitor system resources

   ```bash
   # Monitor memory usage
   top -p $(pgrep -f "python bot.py")
   ```

4. **Update Dependencies**: Ensure discord.py and other packages are up to date
   ```bash
   pip install --upgrade discord.py python-dotenv
   ```

### Message Content Not Accessible

**Problem**: Bot can't read message content for thread naming.

**Symptoms**:

- Threads are created with generic names like "Discussion Thread"
- Console output shows empty message content

**Solutions**:

1. **Enable Message Content Intent**: This is a privileged intent

   - Discord Developer Portal → Bot → Privileged Gateway Intents
   - Enable "Message Content Intent"

2. **Verify Bot Application**: Ensure your bot is verified if needed
   - Large bots may need verification to access message content

## 🐛 Debug Mode

Enable debug logging for detailed troubleshooting information.

### Enabling Debug Mode

Set the log level to DEBUG in your `.env` file:

```env
LOG_LEVEL=DEBUG
```

### Debug Output

Debug mode provides verbose logging including:

- **Message processing details**: Every message the bot processes
- **Permission validation results**: Detailed permission checks
- **API call information**: Discord API interactions
- **Error stack traces**: Full error details with line numbers

### Example Debug Output

```
2025-06-24 12:34:56 - DEBUG - Processing reply from user123 in #general
2025-06-24 12:34:56 - DEBUG - Validating permissions in channel #general
2025-06-24 12:34:56 - DEBUG - Permission check: Create Public Threads = True
2025-06-24 12:34:56 - DEBUG - Creating thread with name: "What's your favorite Python library"
2025-06-24 12:34:57 - DEBUG - Thread created successfully: ID 1234567890
```

### Console Output

All logging output is displayed in the console/terminal where you run the bot.

**Viewing Console Output:**

- Run the bot in a terminal and monitor the output in real-time
- Error messages, warnings, and debug information appear immediately
- Use terminal scrollback to review recent messages
- Consider using terminal multiplexers like `screen` or `tmux` for persistent sessions

**Capturing Console Output:**

```bash
# Run bot and save output to a file for analysis
python bot.py 2>&1 | tee bot_output.txt

# Run bot in background and redirect output
nohup python bot.py > bot_output.txt 2>&1 &
```

## ⚡ Performance Considerations

### Large Servers

For servers with high message volume:

- **Monitor CPU usage**: High reply frequency may increase processing load
- **Watch memory consumption**: Bot memory usage scales with activity
- **Consider rate limiting**: Discord has API rate limits that may affect responsiveness

### Rate Limiting

Discord API has rate limits that may affect bot performance:

- **Global rate limit**: 50 requests per second
- **Per-route rate limits**: Vary by endpoint
- **Thread creation limits**: May be limited in high-traffic scenarios

**Monitoring Rate Limits**:

Watch the console output for these messages:

```
Rate limited for X seconds
429 Too Many Requests
WARNING - Rate limited, retrying in X seconds
```

### Memory Usage

Monitor bot memory usage, especially in large servers:

```bash
# Check memory usage
ps aux | grep "python bot.py"

# Monitor over time
watch -n 5 'ps aux | grep "python bot.py"'
```

### Optimization Tips

1. **Restart periodically**: Consider restarting the bot daily to clear memory
2. **Monitor console output**: Watch for patterns in error messages or warnings
3. **Update regularly**: Keep dependencies updated for performance improvements

## 🆘 Getting Help

If you're still experiencing issues after trying the solutions above:

### Before Seeking Help

1. **Check the [Issues](https://github.com/wei/thread-it/issues)** page for similar problems
2. **Search closed issues** for resolved problems
3. **Try the latest version** of the bot

### Creating a Support Issue

When creating a new issue, include:

**System Information**:

- Operating system and version
- Python version (`python --version`)
- Discord.py version (`pip show discord.py`)
- Bot version or commit hash

**Problem Description**:

- Detailed description of the problem
- Steps to reproduce the issue
- Expected behavior vs actual behavior

**Console Output**:

Include relevant console output from when the issue occurred:

- Copy error messages, warnings, or stack traces from the terminal
- Include timestamps if available
- Remove sensitive information like tokens or server IDs
- Show the context around the error (a few lines before and after)

**Configuration** (remove sensitive data):

```env
# Your .env file (without tokens)
LOG_LEVEL=DEBUG
```

### Community Support

- **GitHub Issues**: [Report bugs or ask questions](https://github.com/wei/thread-it/issues)
- **Documentation**: [Design Specification](DESIGN_SPECIFICATION.md)
- **Discord.py Docs**: [Official discord.py documentation](https://discordpy.readthedocs.io/)

## 📊 Log Analysis

### Understanding Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General information about bot operation
- **WARNING**: Something unexpected happened but bot continues
- **ERROR**: Serious problem that prevented an operation
- **CRITICAL**: Very serious error that may stop the bot

### Common Log Patterns

**Successful Operation**:

```
INFO - Successfully processed reply: created thread 'Discussion about Python'
```

**Permission Issues**:

```
WARNING - Missing permission 'Create Public Threads' in channel #general
```

**API Errors**:

```
ERROR - Failed to create thread: 403 Forbidden (error code: 50013)
```

**Rate Limiting**:

```
WARNING - Rate limited for 2.5 seconds, retrying...
```

---

## 🎯 Quick Diagnostic Checklist

When troubleshooting, check these items in order:

1. ✅ **Bot is online** in Discord
2. ✅ **Message Content Intent** is enabled
3. ✅ **Required permissions** are granted
4. ✅ **Bot token** is valid and current
5. ✅ **Channel supports threads** (text channels only)
6. ✅ **No rate limiting** in console output
7. ✅ **Latest dependencies** are installed
8. ✅ **Debug logging** is enabled for detailed info

If all items are checked and issues persist, create a detailed issue report with console output and system information.

---

**Need more help?** Check the [Contributing Guide](CONTRIBUTING.md) for development-related questions or the main [README](../README.md) for general information.
