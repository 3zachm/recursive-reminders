import discord
from discord import Embed
import utils.utils as utils

empty = Embed.Empty

def general_embed(title = empty, description = empty, timestamp = empty, color = empty, footer_text = empty, footer_icon_url = empty):
    embed=Embed(
        title=title, description=description, timestamp = timestamp, color=color)
    embed.set_footer(text=footer_text, icon_url=footer_icon_url)
    return embed

def in_progress(ctx):
    embed=discord.Embed(
    title='You already have a reminder in progress',
    color=0xcc0000)
    return embed

def reminder_set(ctx, pfx, t):
    user = ctx.message.author
    embed=discord.Embed(
        title="Success! You will be reminded every " + str(int(t/60)) + " minutes",
        description='Do **' + pfx + 'stop** to cancel current and further reminders',
        timestamp = ctx.message.created_at, color = 0x00CC66)
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def reminder_cancel(ctx):
    user = ctx.message.author
    embed=discord.Embed(
        title="Your reminder was cancelled",
        color=0xcc0000)
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def reminder_none(ctx, pfx):
    user = ctx.message.author
    embed=discord.Embed(
        title='You have no reminder in progress',
        description='One can be made with **' + pfx +'remindme [minutes]**',
        timestamp = ctx.message.created_at,
        color=0x6f02cf)
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def reminder_list(ctx, rqs):
    user = ctx.message.author
    rqPages = list(utils.split_array(rqs, 10))
    embed_pages = []
    # a single embed
    embed=discord.Embed(
        title="**Reminders**",
        description="All your active reminders are shown below")
    embed.set_author(name=user.name, icon_url=user.avatar_url)
    embed.set_footer(text="Page 1/" + str(len(rqPages)))
    try:
        temprq = rqPages[0]
    except IndexError:
        return embed
    i = 1
    for rq in temprq:
        embed.add_field(name="#" + str(i) + " | " + rq['name'], value="Length: " + str(rq['time']/60) + "m", inline=False)
        i += 1
    return embed

def timer_end(ctx, pfx, t):
    user = ctx.message.author
    embed=discord.Embed(
        title=str(int(t/60)) + " minutes have passed!",
        description="To cancel further reminders, do " + pfx + "stop",
        color=0xedc707,
        timestamp=ctx.message.created_at)
    embed.set_author(name=user.name + "", icon_url=user.avatar_url)
    return embed

def prefix_current(ctx, pfx):
    embed=discord.Embed(
        title="My prefix is ``" + pfx + "`` for this guild",
        description="If you have prefix conflicts, mention me followed by a new prefix!" + 
        "\nOnly single letter prefixes can be applied this way for exception reasons",
        color=0x00CC66)
    return embed

def prefix_change(ctx, pfx):
    embed=discord.Embed(
        title="Success!",
        description="Prefix changed to ``" + pfx + "``",
        color=0x00CC66)
    return embed