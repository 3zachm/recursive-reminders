import datetime
import discord
import configparser, os
import io
import asyncio
import json
from threading import Event
from discord.ext import commands, tasks
from datetime import date

config = configparser.ConfigParser()
dn = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(dn + '/config.ini'):
    config['discord'] = {'token': ''}
    config.write(open(dn + '/config.ini', 'w'))
    print('Config generated. Please edit it with your token.')
    quit()
if not os.path.exists(dn + '/prefixes.json'):
    with open('prefixes.json', 'w') as p:
        json.dump({}, p)

with open(dn + "/config.ini") as c:
    discord_config = c.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_file(io.StringIO(discord_config))

defaultPrefix = '!'

def initPrefix(id):
    with open('prefixes.json', 'r') as p:
        prefixes = json.load(p)
    prefixes[str(id)] = defaultPrefix
    with open('prefixes.json', 'w') as p:
        json.dump(prefixes, p, indent=4)

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as p:
        prefixes = json.load(p)
    try:
        pfx = prefixes[str(message.guild.id)]
    except:
        initPrefix(message.guild.id)
        with open('prefixes.json', 'r') as p:
            prefixes = json.load(p)
        pfx = prefixes[str(message.guild.id)]
    return pfx

botToken = config.get('discord', 'token')
bot = commands.Bot(command_prefix = get_prefix)
requestNum = 0
remindList = []

@bot.event
async def on_guild_join(guild):
    initPrefix(guild.id)

@bot.command(name="prefix")
@commands.has_permissions(administrator=True)
async def prefix(ctx, prefix):
    with open('prefixes.json', 'r') as p:
        prefixes = json.load(p)
    prefixes[str(ctx.guild.id)] = prefix
    with open('prefixes.json', 'w') as p:
        json.dump(prefixes, p, indent=4)
    user = ctx.message.author
    embed=discord.Embed(
            title="Success!",
            description="Prefix changed to " + prefix,
            timestamp = ctx.message.created_at,
            color=0x00CC66)
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    await ctx.send(embed=embed)

@bot.command(name="remindme")
async def remindme(ctx, t):
    global requestNum
    t = int(t) * 60
    user = ctx.message.author
    if user.id in (i[0] for i in remindList):
        embed=discord.Embed(
            title='You already have a reminder in progress',
            color=0xcc0000)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    else:
        requestNum += 1
        remindList.append([user.id, requestNum])
        embed=discord.Embed(
            title="Success! You will be reminded every " + str(int(t/60)) + " minutes",
            description='Do **!stop** to cancel current and further reminders',
            timestamp = ctx.message.created_at, color = 0x00CC66)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)
        timer_task = asyncio.create_task(timer(ctx, t, user.id, requestNum))

@bot.command(name="stop")
async def stop(ctx):
    user = ctx.message.author
    if user.id in (i[0] for i in remindList):
        index = return2DIndex(user.id, remindList, 0)
        remindList[index][0] = 0
        embed=discord.Embed(
            title="Your reminder was cancelled",
            timestamp = ctx.message.created_at,
            color=0xcc0000)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(
            title='You have no reminder in progress',
            description='One can be made with **!remindme [minutes]**',
            timestamp = ctx.message.created_at,
            color=0x6f02cf)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)

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
                    description='Do **!stop** to cancel current and further reminders',
                    timestamp = ctx.message.created_at,
                    color=0x000000)
                embed.set_footer(text=userA.name, icon_url=userA.avatar_url)
                await ctx.send("<@!" + str(userA.id) + ">", embed=embed)
    index = return2DIndex(0, remindList, 0)
    remindList.pop(index)

#TODO help command, command exceptions

def return2DIndex(key, arr, in2D):
    i = [i for i in arr if key in i][in2D]
    return arr.index(i)

bot.run(botToken)
