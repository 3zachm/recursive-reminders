import json
import utils.file_manager as files

def owner_check(ctx):
    with open(files.owners_loc(), 'r') as r:
        owner_list = json.load(r)
    for owner in owner_list['DISCORD_IDS']:
        if owner['id'] == ctx.message.author.id:
            return True
    return False