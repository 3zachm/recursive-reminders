import configparser
import io
import json
import utils.file_manager as files

help_help = "Shows this help menu"
help_args = ""
invite_help = "Gives link to invite the bot"
invite_args = ""
owners_help = "Lists bot owner name and IDs"
owners_args = ""
ping_help = "Responds with command processing latency"
ping_args = ""
prefix_help = "Shows current prefix or changes it to the given argument"
prefix_args = "[prefix]"
reminder_help = "Base command (alias works with subcommands)"
reminder_args = ""
reminder_add_help = "Adds a re-occuring reminder for the specified time under the given name"
reminder_add_args = "[mins] [name]"
reminder_list_help = "Displays all your current reminders and their current IDs"
reminder_list_args = ""
reminder_move_help = "Moves specified request to the current channel or DM\nIf you have only one reminder, no ID is needed."
reminder_move_args = "[id]"
reminder_wait_help = "Toggles waiting for a reaction before counting down again (off by default)\nIf you have only one reminder, no ID is needed."
reminder_wait_args = "[id]"
reminder_stop_help = "Stops the reminder ID which can be seen in your list\nIf you have only one reminder, no ID is needed.\nUsing `all` instead of an ID cancels all current reminders"
reminder_stop_args = "[id]"
uptime_help = "Responds with uptime of the server and bot/shard"
uptime_args = ""

# hide commands from help menu generator
hide_help = ['system', 'system pt', 'system fstop', 'system global_dm', 'evaluate', 'help']

def owner_check(ctx):
    with open(files.owners_loc(), 'r') as r:
        owner_list = json.load(r)
    return any(owner['id'] == ctx.message.author.id for owner in owner_list['DISCORD_IDS'])

def eval_check(ctx):
    with open(files.config_loc()) as c:
        discord_config = c.read()
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read_file(io.StringIO(discord_config))
    enable_eval = config.getboolean('python', 'enable_eval')

    return bool(ctx.message.author.id == 106188449643544576 and enable_eval)