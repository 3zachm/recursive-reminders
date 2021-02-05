# recursive-reminders

[![CodeFactor](https://www.codefactor.io/repository/github/3zachm/recursive-reminders/badge)](https://www.codefactor.io/repository/github/3zachm/recursive-reminders) [![Maintainability](https://api.codeclimate.com/v1/badges/047a379134cb872d9743/maintainability)](https://codeclimate.com/github/3zachm/recursive-reminders/maintainability)

**Public soon!** (a couple days at most)
Global default prefix is ! but can be changed in generated config.

## Commands

- ``!reminder|r add [minutes] [name (string)]`` - Sends a ping to the user every given minute(s)
- ``!reminder|r list`` - Shows list of all current reminders
- ``!reminder|r stop [id]`` - Stops the reminder loop and any in-progress timer for the user.
- ``!prefix [char]`` - Changes prefix, works on per-guild basis.
- ``!help`` - Displays this in a cleaner format
- ``@bot_mention`` - Shows current guild prefix
- ``@bot_mention [char]`` - Alternative prefix change

Reminders have AFK checks in place that require a reaction before the next ping occurence
Likewise, you can also stop them with a reaction.

![Timer example](https://i.imgur.com/vLQk9oQ.png)