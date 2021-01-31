# recursive-reminders

[![CodeFactor](https://www.codefactor.io/repository/github/3zachm/recursive-reminders/badge)](https://www.codefactor.io/repository/github/3zachm/recursive-reminders)

WIP! Approaching stable enough for public hosting as of recent.\
Global default prefix is ! but can be changed in generated config.

- ``!reminder|r add [minutes] [name (string)]`` - Sends a ping to the user every given minute(s)
- ``!reminder|r list`` - Shows list of all current reminders
- ``!reminder|r stop [id]`` - Stops the reminder loop and any in-progress timer for the user.
- ``!prefix [char]`` - Changes prefix, works on per-guild basis.
- ``!help`` - Displays this in a cleaner format
- ``@bot_mention`` - Shows current guild prefix
- ``@bot_mention [char]`` - Alternative prefix change
