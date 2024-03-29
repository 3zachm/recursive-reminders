import json
import utils.file_manager as files
import utils.utils as utils


def create(ctx, loc, rqname, time):
    userid = ctx.message.author.id
    request = ctx.message.id
    if ctx.guild is None:
        guild_name = ""
        channel = 1
    else:
        guild_name = ctx.guild.name
        channel = ctx.channel.id
    data = {"user": userid, "request": request, "name": rqname, "time": time, "guild": guild_name, "channel": channel, "source": request, "wait": False, "added": 0}
    files.make_json(loc + str(userid) + '_' + str(request) + '.json', data) # ./id_rq.json
    return data

def remove(path, request_id, arr):
    timer_task = arr[utils.return2DIndex(request_id, arr)][1]
    timer_task.cancel()
    del arr[utils.return2DIndex(request_id, arr)]
    files.delete_json(path, request_id)

def retrieve_list(userid, path):
    request_list = []
    request_files = files.get_json(userid, path)
    for file in request_files:
        with open(file, 'r') as r:
            request = json.load(r)
        request_list.append(request)
    return request_list

def retrieve_json_id(path, userid, request_id):
    request_json = files.get_json(str(userid) + "_" + str(request_id), path)[0]
    with open(request_json, 'r') as r:
        rq_json = json.load(r)
    return rq_json

def get_index(userid, path, rq_json):
    arr = retrieve_list(userid, path)
    return arr.index(rq_json)

def retrieve_json(userid, path, request):
    request_files = files.get_json(userid, path)
    request_json = request_files[request - 1]
    with open(request_json, 'r') as r:
        request = json.load(r)
    return request

def edit_json_val(userid, path, request_id, key, value):
    rq_json = files.get_json(str(userid) + "_" + str(request_id), path)[0]
    with open(rq_json, 'r+') as w:
        rq = json.load(w)
        rq[key] = value
        w.seek(0)
        json.dump(rq, w, indent=4)
        w.truncate()
    return rq