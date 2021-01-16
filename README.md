## recursive-reminders
[![CodeFactor](https://www.codefactor.io/repository/github/3zachm/recursive-reminders/badge)](https://www.codefactor.io/repository/github/3zachm/recursive-reminders)

Recently merged rewrite to master, but UI/commands are still not fully finished.

WIP! Actually fleshing this out, will be hosted publically when deemed stable enough.\
Global default prefix is ! but can be changed in generated config.

- ``!remindme [minutes] [name (string)]`` - Sends a ping to the user every given minute(s)
- ``!remindlist`` - Shows list of all current reminders
- ``!stop [id]`` - Stops the reminder loop and any in-progress timer for the user.
- ``!prefix [char]`` - Changes prefix, works on per-guild basis.
- ``@bot_mention`` - Shows current guild prefix
- ``@bot_mention [char]`` - Alternative prefix change
