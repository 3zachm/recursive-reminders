import datetime
import discord
import configparser
import os
import io
import asyncio
import json
from threading import Event
from discord.ext import commands, tasks
from datetime import date

config = configparser.ConfigParser()
# script location
dn = os.path.dirname(os.path.realpath(__file__))

# generate empty config files
if not os.path.exists(dn + '/config.ini'):
    config['discord'] = {'token': '', 'default_prefix': '!'}
    config.write(open(dn + '/config.ini', 'w'))
    print('Config generated. Please edit it with your token.')
    quit()
if not os.path.exists(dn + '/prefixes.json'):
    with open('prefixes.json', 'w') as w:
        json.dump({}, w)

# open config file
with open(dn + "/config.ini") as c:
    discord_config = c.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_file(io.StringIO(discord_config))

defaultPrefix = config.get('discord', 'default_prefix')

# initializes a server in the prefix file
def initPrefix(serverID):
    with open('prefixes.json', 'r') as r:
        prefixes = json.load(r)
    prefixes[str(serverID)] = defaultPrefix
    with open('prefixes.json', 'w') as w:
        json.dump(prefixes, w, indent=4)

def get_prefix(bot, message):
    if not message.guild:
        return ""
    with open('prefixes.json', 'r') as r:
        prefixes = json.load(r)
    try:
        pfx = prefixes[str(message.guild.id)]
    except KeyError:
        initPrefix(message.guild.id)
        with open('prefixes.json', 'r') as r:
            prefixes = json.load(r)
        pfx = prefixes[str(message.guild.id)]
    return pfx

botToken = config.get('discord', 'token')
bot = commands.Bot(command_prefix = get_prefix)
bot.requestNum = 0
remindList = []

@bot.event
async def on_ready():
    print('Running...')
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    # generate bot owner
    if not os.path.exists(dn + '/owners.json'):
        ids = {"DISCORD_IDS": []}
        ids["DISCORD_IDS"].append({"name": bot.appinfo.owner.name, 'id': bot.appinfo.owner.id})
        with open('owners.json', 'w') as w:
            json.dump(ids, w, indent=4)

@bot.event
async def on_guild_join(guild):
    initPrefix(guild.id)

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
                embed=discord.Embed(
                    title="My prefix is ``" + pfx + "`` for this guild",
                    description="If you have prefix conflicts, mention me followed by a new prefix!" + 
                    "\nOnly single letter prefixes can be applied this way for exception reasons",
                    #timestamp = ctx.message.created_at,
                    color=0x00CC66)
                #embed.set_footer(text=user.name, icon_url=user.avatar_url)
                await ctx.send(embed=embed)
    await bot.process_commands(message)

@bot.command(name="prefix")
@commands.has_permissions(administrator=True)
async def prefix(ctx, prefix): # add prefix check through prefix only
    with open('prefixes.json', 'r') as r:
        prefixes = json.load(r)
    prefixes[str(ctx.guild.id)] = prefix
    with open('prefixes.json', 'w') as w:
        json.dump(prefixes, w, indent=4)
    user = ctx.message.author
    if prefix == '':
        prefix = 'None'
    embed=discord.Embed(
            title="Success!",
            description="Prefix changed to ``" + prefix + "``",
            #timestamp = ctx.message.created_at,
            color=0x00CC66)
    #embed.set_footer(text=user.name, icon_url=user.avatar_url)
    await ctx.send(embed=embed)

@bot.command(name="remindme")
async def remindme(ctx, t):
    t = int(t) * 60
    user = ctx.message.author
    if user.id in (i[0] for i in remindList):
        embed=discord.Embed(
            title='You already have a reminder in progress',
            color=0xcc0000)
        #embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    else:
        bot.requestNum += 1
        remindList.append([user.id, bot.requestNum])
        embed=discord.Embed(
            title="Success! You will be reminded every " + str(int(t/60)) + " minutes",
            description='Do **' + str(get_prefix(bot=bot, message=ctx.message)) +'stop** to cancel current and further reminders',
            timestamp = ctx.message.created_at, color = 0x00CC66)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)
        timer_task = asyncio.create_task(timer(ctx, t, user.id, bot.requestNum))

@bot.command(name="stop")
async def stop(ctx):
    user = ctx.message.author
    if user.id in (i[0] for i in remindList):
        index = return2DIndex(user.id, remindList, 0)
        remindList[index][0] = 0
        embed=discord.Embed(
            title="Your reminder was cancelled",
            #timestamp = ctx.message.created_at,
            color=0xcc0000)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(
            title='You have no reminder in progress',
            description='One can be made with **' + get_prefix(bot=bot, message=ctx.message) +'remindme [minutes]**',
            timestamp = ctx.message.created_at,
            color=0x6f02cf)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)

# sort of inefficient? should invoke a cancel in the stop command too
async def timer(ctx, t, user, rq):
    userA = ctx.message.author
    index = return2DIndex(user, remindList, 0)
    while(remindList[index][1] == rq):
        await asyncio.sleep(t)
        if user in (i[0] for i in remindList):
            index = return2DIndex(user, remindList, 0)
            if remindList[index][1] == rq:
                embed=discord.Embed(
                    title=str(int(t/60)) + " minutes are up!",
                    description='Do **' + get_prefix(bot=bot, message=ctx.message) +'stop** to cancel current and further reminders',
                    timestamp = ctx.message.created_at,
                    color=0x000000)
                embed.set_footer(text=userA.name, icon_url=userA.avatar_url)
                await ctx.send("<@!" + str(userA.id) + ">", embed=embed)
    index = return2DIndex(0, remindList, 0)
    remindList.pop(index)

def return2DIndex(key, arr, in2D):
    i = [i for i in arr if key in i][in2D]
    return arr.index(i)

bot.run(botToken)
