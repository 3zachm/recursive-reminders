import configparser
import os
import io
import json

def make_config(path):
    config = configparser.ConfigParser()
    if not os.path.exists(path):
        config['discord'] = {'token': '', 'default_prefix': '!'}
        config['python'] = {'generate_logs': True}
        config.write(open(path, 'w'))
        print('Config generated. Please edit it with your token.')
        quit()

def make_prefixes(path):
    if not os.path.exists(path):
        with open(path, 'w') as w:
            json.dump({}, w)

def make_owners(path, bot):
    if not os.path.exists(path):
        ids = {"DISCORD_IDS": []}
        ids["DISCORD_IDS"].append({"name": bot.appinfo.owner.name, 'id': bot.appinfo.owner.id})
        with open(path, 'w') as w:
            json.dump(ids, w, indent=4)

# consider moving other writing operations here at the end of dev