import asyncio
import json
import io
import discord
from asyncio.coroutines import coroutine
import utils.file_manager as files
import utils.utils as utils


def create(loc, userid, request, time):
    data = {"user": userid, "request": request, "time": time}
    files.make_json(loc + str(userid) + '_' + str(request) + '.json', data) # ./id_rq.json

# CURRENTLY DEBUG--Actually replace the array system -midnight zach
def remove(request, arr):
    timer_task = arr[utils.return2DIndex(request, arr, 0)][1]
    timer_task.cancel()