import datetime
from asyncio.coroutines import coroutine
import discord
import configparser
import os
import io
import asyncio
import json
import logging
import time
from threading import Event
from discord.ext import commands, tasks
from datetime import date
import utils.embed_generator as embeds
import utils.file_manager as files
import utils.log_manager as logs
import utils.request_manager as requests
import utils.utils as utils

config = configparser.ConfigParser()
script_location = os.path.dirname(os.path.realpath(__file__))

# generate empty config files
files.make_config(script_location + '/config.ini')
files.make_prefixes(script_location + '/prefixes.json')
files.make_dir(script_location + '/requests/')

# open config file
with open(script_location + '/config.ini') as c:
    discord_config = c.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_file(io.StringIO(discord_config))

try:
    defaultPrefix = config.get('discord', 'default_prefix')
    generateLogs = config.getboolean('python', 'generate_logs')
except (configparser.NoSectionError, configparser.NoOptionError) as e:
    print(e)
    print("Ensure config file has all entries present. If you recently pulled an update, consider regenerating the config")
    quit()

#logging
if generateLogs:
    logger = logs.init_logs(script_location + '/logs/')

# initializes a server in the prefix file
def initPrefix(serverID):
    with open(script_location + '/prefixes.json', 'r') as r:
        prefixes = json.load(r)
    prefixes[str(serverID)] = defaultPrefix
    with open(script_location + '/prefixes.json', 'w') as w:
        json.dump(prefixes, w, indent=4)

def get_prefix(bot, message):
    if not message.guild:
        return ""
    with open(script_location + '/prefixes.json', 'r') as r:
        prefixes = json.load(r)
    try:
        pfx = prefixes[str(message.guild.id)]
    except KeyError:
        initPrefix(message.guild.id)
        with open(script_location + '/prefixes.json', 'r') as r:
            prefixes = json.load(r)
        pfx = prefixes[str(message.guild.id)]
    return pfx

botToken = config.get('discord', 'token')
bot = commands.Bot(command_prefix = get_prefix)
bot.coroutineList = []

@bot.event
async def on_ready():
    print('Running...')
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    # generate bot owner
    files.make_owners(script_location + '/owners.json', bot)

@bot.event
async def on_guild_join(guild):
    initPrefix(guild.id)
    logs.log("Joined \"" + guild.name + "\" - " + str(guild.id), logger)

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    msg = message.content
    if (bot.user.mentioned_in(message)):
        if message.mentions[0] == bot.user:
            try:
                firstMention = msg[0 : msg.index(' ')]
            except ValueError:
                firstMention = ''
            if firstMention == (f'<@!{bot.user.id}>') and ctx.message.author.guild_permissions.administrator: # if mention is first and has space
                index = msg.index(' ')
                await prefix(ctx, msg[index + 1 : index + 2]) # i'm bad at python
            else:
                pfx = str(get_prefix(bot=bot, message=message))
                if pfx == '':
                    pfx = 'None'
                embed = embeds.prefix_current(ctx, guild_prefix(ctx))
                await ctx.send(embed=embed)
    await bot.process_commands(message)

@bot.command(name="prefix")
@commands.has_permissions(administrator=True)
async def prefix(ctx, prefix): # add prefix check through prefix only
    with open(script_location + '/prefixes.json', 'r') as r:
        prefixes = json.load(r)
    prefixes[str(ctx.guild.id)] = prefix
    with open(script_location + '/prefixes.json', 'w') as w:
        json.dump(prefixes, w, indent=4)
    user = ctx.message.author
    if prefix == '':
        prefix = 'None'
    embed = embeds.prefix_change(ctx, prefix)
    await ctx.send(embed=embed)

@bot.command(name="remindme")
async def remindme(ctx, t, *, rqname):
    t = int(t) * 60
    user = ctx.message.author
    requests.create(script_location + '/requests/', user.id, ctx.message.id, rqname, t)
    embed = embeds.reminder_set(ctx, guild_prefix(ctx), t)
    await ctx.send(embed=embed)
    timer_task = asyncio.create_task(timer(ctx, ctx.message.id, t), name=ctx.message.id)
    bot.coroutineList.append([ctx.message.id, timer_task])

@bot.command(name="remindlist")
async def remindlist(ctx):
    requests_list = requests.retrieve_list(ctx.message.author.id, script_location + '/requests/')
    embed = embeds.reminder_list(ctx, requests_list)
    await ctx.send(embed=embed)

@bot.command(name="stop")
async def stop(ctx, request):
    user = ctx.message.author
    if requests.retrieve_list(user.id, script_location + '/requests/') == []:
        embed=embeds.reminder_none(ctx, guild_prefix(ctx))
        await ctx.send(embed=embed)
    else:
        requests.remove(user.id, script_location + '/requests/', int(request), bot.coroutineList)
        embed = embeds.reminder_cancel(ctx)
        await ctx.send(embed=embed)

# add information for embed
async def timer(ctx, rq, t):
    user = ctx.message.author
    while(True):
        await asyncio.sleep(t)
        embed=embeds.timer_end(ctx=ctx, pfx=guild_prefix(ctx), t=t)
        await ctx.send("<@!" + str(user.id) + ">", embed=embed)

# offhand because discord.py needs get_prefix to have args
def guild_prefix(ctx):
    return get_prefix(bot=bot, message=ctx.message)

bot.run(botToken)
