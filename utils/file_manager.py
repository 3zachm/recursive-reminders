import configparser
import os
import io
import json
import glob

script_dir = ''

def prefix_loc():
    return script_dir + '/prefixes.json'

def config_loc():
    return script_dir + '/config.ini'

def owners_loc():
    return script_dir + '/owners.json'

def request_dir():
    return script_dir + '/requests/'

def logs_dir():
    return script_dir + '/logs/'

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
        make_json(path, {})

def make_owners(path, bot):
    if not os.path.exists(path):
        ids = {"DISCORD_IDS": []}
        ids["DISCORD_IDS"].append({"name": bot.appinfo.owner.name, 'id': bot.appinfo.owner.id})
        make_json(path, ids)

def make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def make_json(path, data):
    with open(path, 'w') as w:
        json.dump(data, w, indent=4)

def delete_json(path, rq):
    for file in glob.glob(path + '*' + str(rq) + '.json'):
        if os.path.exists(file):
            os.remove(file)

def delete_contents(path):
    for file in glob.glob(path + '*'):
        os.remove(file)

def get_json(key, path):
    arr = []
    for file in glob.glob(path + str(key) + '*.json'):
        arr.append(file)
    return arr
# consider moving other writing operations here at the end of dev