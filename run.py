import datetime
import discord
import configparser, os
import io
import asyncio
from threading import Event
from discord.ext import commands, tasks
from datetime import date

config = configparser.ConfigParser()

if not os.path.exists('config.ini'):
    config['discord'] = {'token': ''}
    config.write(open('config.ini', 'w'))
    print('Config generated. Please edit it with your token.')
    quit()

with open("config.ini") as c:
    discord_config = c.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_file(io.StringIO(discord_config))

botToken = config.get('discord', 'token')
bot = commands.Bot(command_prefix = '!')
requestNum = 0
remindList = []

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
        i = [i for i in remindList if user.id in i][0]
        index = remindList.index(i)
        remindList[index][0] = 0
        embed=discord.Embed(
            title="Your reminder was cancelled",
            timestamp = ctx.message.created_at,
            color=0x6f02cf)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(
            title='You have no reminder in progress',
            description='One can be made with **!remind [minutes]**',
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

def return2DIndex(key, arr, in2D):
    i = [i for i in arr if key in i][in2D]
    return arr.index(i)

bot.run(botToken)
