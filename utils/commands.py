import json
import utils.file_manager as files

help_help = "Shows this help menu"
help_args = ""
prefix_help = "Shows current prefix or changes it to the given argument"
prefix_args = "[prefix]"
reminder_help = "Displays the available reminder commands" # actually implement
reminder_args = "[add/stop/list]"
reminder_add_help = "Adds a re-occuring reminder for the specified time under the given name"
reminder_add_args = "[mins] [name]"
reminder_list_help = "Displays all your current reminders and their current IDs"
reminder_list_args = ""
reminder_stop_help = "Stops the reminder ID which can be seen in your list"
reminder_stop_args = "[id]"

def owner_check(ctx):
    with open(files.owners_loc(), 'r') as r:
        owner_list = json.load(r)
    for owner in owner_list['DISCORD_IDS']:
        if owner['id'] == ctx.message.author.id:
            return True
    return False