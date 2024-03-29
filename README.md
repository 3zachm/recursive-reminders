# recursive-reminders

[![CodeFactor](https://www.codefactor.io/repository/github/3zachm/recursive-reminders/badge)](https://www.codefactor.io/repository/github/3zachm/recursive-reminders) [![Maintainability](https://api.codeclimate.com/v1/badges/047a379134cb872d9743/maintainability)](https://codeclimate.com/github/3zachm/recursive-reminders/maintainability)

~~Public invite [here](https://3zachm.dev/youmu/)!~~
Bot is too niche to rewrite with buttons on the discord.py library, so I'm no longer publicly hosting it

Global default prefix is `!` but can be changed in generated config.

## Commands

- `!reminder|r add [minutes (int)] [name (string)]` - Sends a ping to the user every given minute(s)
- `!reminder|r list` - Shows list of all current reminders
- `!reminder|r move [id]` - Moves the reminder to the current channel/DM (ID not needed if only one reminder)
- `!reminder|r stop [id]` - Stops the reminder loop and any in-progress timer for the user (above also applies)
- `!reminder|r stop all` - Stops all personal reminders
- `!prefix [char/str]` - Changes prefix, works on per-guild basis
- `!help` - Displays this in a cleaner format
- `!owners` - Lists users in owners.json
- `!invite` - Gives invite to bot (by default the public link, change as needed)
- `!ping|test` - Returns discord message delay and heartbeat latency
- `!system|sys pt` - Admin permission test
- `uptime` - Responds with uptime of server/bot
- `@bot_mention` - Shows current guild prefix
- `@bot_mention [char]` - Alternative prefix change

**Admin `!system|sys`**

- `fstop [reminder ID]` - Force stop a reminder based on its ID
- `eval [Python Code]` - Can be enabled as needed in `config.ini` even while running.
- `global_dm` - Message anyone with a running reminder. Sets bot into "reset" mode.

Reminders have AFK checks in place that require a reaction before the next ping occurence\
Likewise, you can also stop them with a reaction.

![Timer example](https://i.imgur.com/vLQk9oQ.png)

## Requirements

Built on **Python 3.9.0**, get `discord.py`, `psutils` (for uptime), and `windows-curses` if needed

Eval is **hardcoded** with a user ID for security in commands.py and evaluate(), so if you're self-hosting change that
