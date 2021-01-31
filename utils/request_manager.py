import asyncio
import json
import io
import discord
from asyncio.coroutines import coroutine
import utils.file_manager as files
import utils.utils as utils


def create(loc, userid, request, rqname, time):
    data = {"user": userid, "request": request, "name": rqname, "time": time}
    files.make_json(loc + str(userid) + '_' + str(request) + '.json', data) # ./id_rq.json
    return data

def remove(userid, path, request, arr):
    # get the request number (chronological)
    request = retrieve_json(userid, path, request)['request']
    timer_task = arr[utils.return2DIndex(request, arr, 0)][1]
    timer_task.cancel()
    del arr[utils.return2DIndex(request, arr, 0)]
    files.delete_json(path, request)

def retrieve_list(userid, path):
    request_list = []
    request_files = files.get_json(userid, path)
    for file in request_files:
        with open(file, 'r') as r:
            request = json.load(r)
        request_list.append(request)
    return request_list

def retrieve_json(userid, path, request):
    request_files = files.get_json(userid, path)
    request_json = request_files[request - 1]
    with open(request_json, 'r') as r:
        request = json.load(r)
    return request