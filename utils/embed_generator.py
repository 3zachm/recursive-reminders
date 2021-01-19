import asyncio
import discord
from discord import Embed
import utils.utils as utils

empty = Embed.Empty
all_control_emoji = ["⏮", "⬅️", "➡️", "⏭"] # steal from anigame tbh


def reminder_set(ctx, pfx, t, rqname):
    user = ctx.message.author
    embed=discord.Embed(
        title="Success! You will be reminded every " + str(int(t/60)) + " minutes",
        description='You created a reminder for ' + rqname + '\nDo ``' + pfx + 'stop [number]`` to cancel current and further reminders',
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
        description='One can be made with **' + pfx +'remindme [minutes] [name]**',
        timestamp = ctx.message.created_at,
        color=0x6f02cf)
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def request_length(ctx, var, length):
    embed=discord.Embed(
        title="That " + var + " name is too long :(",
        description="Try to keep it under or equal to " + length + "!")
    return embed

async def reminder_list(ctx, rqs):
    user = ctx.message.author
    rq_pages = list(utils.split_array(rqs, 5))
    embed_list = []
    page_count = 0
    rq_number = 1
    # make more efficient embed
    if len(rq_pages) == 0:
        embed=discord.Embed(
           title="**Reminders**",
           description="You have no active reminders" 
        )
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text="Page 0/0")
        await ctx.send(embed=embed)
        return
    for page in rq_pages:
        embed=discord.Embed(
            title="**Reminders**",
            description="All your active reminders are shown below")
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_footer(text="Page " + str(page_count + 1) + "/" + str(len(rq_pages)))
        try:
            rq_page = page
        except IndexError:
            # handle no reminders
            return embed
        for rq in rq_page:
            embed.add_field(
                name="#" + str(rq_number) + " | " + rq['name'], 
                value="Length: " + str(rq['time']/60) + "m", 
                inline=False)
            rq_number += 1
        embed_list.append(embed)
        page_count += 1
    await embed_pages(ctx, embed_list, 0)

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

def prefix_dms(ctx):
    embed=discord.Embed(
        title="I have no prefix for DMs!",
        description="Simply send the command keyword like ``help``")
    return embed

def prefix_length(ctx):
    embed=discord.Embed(
        title="That prefix is too long",
        description="Anyhing less than 10 characters is more reasonable c:")
    return embed

async def embed_pages(ctx, pages, mode):
    bot = ctx.bot
    pg = 0
    reaction = None
    message = await ctx.send(embed = pages[pg])
    for emoji in all_control_emoji:
        await message.add_reaction(emoji)

    def check(reaction, user):
        return reaction.message.id == message.id and user == ctx.author

    while(True):
        if str(reaction) == '⏮':
            pg = 0
            await reaction.message.edit(embed = pages[pg])
        elif str(reaction) == '⬅️':
            if pg > 0:
                pg -= 1
                await reaction.message.edit(embed = pages[pg])
        elif str(reaction) == '➡️':
            if pg < len(pages) - 1:
                pg += 1
                await reaction.message.edit(embed = pages[pg])
        elif str(reaction) == '⏭':
            pg = len(pages) - 1
            await reaction.message.edit(embed = pages[pg])
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout = 30.0, check = check)
            if ctx.guild is not None:
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            break
    try:
        if ctx.guild is not None:
            await message.clear_reactions()
    except discord.Forbidden:
        # replace with smthn formal
        await ctx.send("I don't have permission to remove reactions :(\nPlease make sure I have the ``Manage Message`` permission")