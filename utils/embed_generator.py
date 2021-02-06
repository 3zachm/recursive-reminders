import asyncio
import discord
from discord import Embed
import utils.utils as utils
import utils.commands as cmds
import utils.request_manager as requests
import utils.file_manager as files

empty = Embed.Empty
all_control_emoji = ["⏮", "⬅️", "➡️", "⏭"]
confirm_control_emoji = ["✅","❌"]

# add aliases
async def help(ctx, pfx, bot):
    cmd_list = []
    embed_list = []
    page_count = 0
    cmd_number = 1
    for cmd in bot.walk_commands():
        cmd_list.append(cmd)
    cmd_pages = list(utils.split_array(cmd_list, 10))
    for page in cmd_pages:
        embed=discord.Embed(
            title="**Commands**",
            description="See a more presentable help list here: (link WIP)"
        )
        embed.set_footer(text="Page " + str(page_count + 1) + "/" + str(len(cmd_pages)))
        try:
            cmd_page = page
        except IndexError:
            # handle no reminders
            return embed
        for cmd in cmd_page:
            alias = ""
            if len(cmd.aliases) > 0:
                alias = "\nAlias: ``" + pfx
                for a in cmd.aliases:
                    alias += a + " "
                alias = alias[:-1] + "``"
            embed.add_field(
                name=pfx + str(cmd) + " " + cmd.description,
                value=cmd.help + alias,
                inline=False
            )
            cmd_number += 1
        embed_list.append(embed)
        page_count += 1
    await embed_pages(ctx, embed_list)

def reminder_base(ctx, pfx, bot):
    embed=discord.Embed(
        title="Reminder commands:",
        description="Make mulltiple recursive reminders up to 12 hour intervals"
    )
    cmd_list = [bot.get_command('reminder add'), bot.get_command('reminder list'), bot.get_command('reminder stop')]
    for cmd in cmd_list:
        embed.add_field(
            name=pfx + str(cmd) + " " + cmd.description,
            value=cmd.help,
            inline=False
        )
    return embed

def reminder_set(ctx, pfx, t, rqname):
    user = ctx.message.author
    embed=discord.Embed(
        title="Success! You will be reminded every " + str(int(t/60)) + " minutes",
        description='You created a recursive reminder for ``' + rqname + '``\nDo ``' + pfx + "reminder|r stop " + cmds.reminder_stop_args + '`` to cancel current and further reminders',
        timestamp = ctx.message.created_at, color = 0x00CC66
    )
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def reminder_cancel(ctx, rq_json):
    user = ctx.message.author
    embed=discord.Embed(
        title="Your reminder for ``" + rq_json["name"] + "`` was cancelled",
        color=0xcc0000
    )
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed


def reminder_cancel_timeout(ctx, rq_json):
    user = ctx.message.author
    embed=discord.Embed(
        title="Your reminder for ``" + rq_json["name"] + "`` was cancelled",
        description="No reaction was received before the next reminder occurence",
        color=0xcc0000
    )
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def reminder_cancel_index(ctx, pfx, rqID):
    user = ctx.message.author
    embed=discord.Embed(
        title="No reminder in your list matches ID " + str(rqID),
        description="Check your current reminder IDs with ``" + pfx + "reminder|r list``",
        color=0xcc0000
    )
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def reminder_none(ctx, pfx):
    user = ctx.message.author
    embed=discord.Embed(
        title='You have no reminder in progress',
        description='One can be made with ``' + pfx + "reminder|r add " + cmds.reminder_add_args + '``',
        timestamp = ctx.message.created_at,
        color=0x6f02cf
    )
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

def request_length(ctx, var, length):
    embed=discord.Embed(
        title="That " + var + " is too long :(",
        description="Try to keep it under or equal to " + length + "!"
    )
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
            description="All your active reminders are shown below"
        )
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
                inline=False
            )
            rq_number += 1
        embed_list.append(embed)
        page_count += 1
    await embed_pages(ctx, embed_list)

def reminder_add_missing(ctx, pfx, bot):
    embed=discord.Embed(
        title="Missing requirements!",
    )
    cmd = bot.get_command('reminder add')
    embed.add_field(
        name=pfx + str(cmd) + " " + cmd.description,
        value=cmd.help + "\n\nExample: ``!r add 20 Raid`` creates a 20 minute timer named Raid",
        inline=False
    )
    return embed

def reminder_stop_missing(ctx, pfx, bot):
    embed=discord.Embed(
        title="Missing requirements!",
    )
    cmd = bot.get_command('reminder stop')
    embed.add_field(
        name=pfx + str(cmd) + " " + cmd.description,
        value="Specify an ID to stop, which can be found in the reminder list",
        inline=False
    )
    return embed

async def timer_end(ctx, pfx, rq_json):
    t = rq_json["time"]
    rq_name = rq_json["name"]
    user = ctx.message.author
    embed=discord.Embed(
        title=str(int(t/60)) + " minutes have passed!",
        description="Your reminder for ``" + rq_name + "`` is up (id " + str(requests.get_index(user.id, files.request_dir(), rq_json) + 1) + ")"
        "\n" +
        "``React``  ✅  to confirm you aren't AFK by the next occurence" +
        "\n``React``  ❌  to stop or do ``" + pfx + "reminder|r stop [id]``",
        color=0xedc707,
        timestamp=ctx.message.created_at
    )
    embed.set_author(name=user.name + "", icon_url=user.avatar_url)
    await timer_react(ctx, embed)

def timer_continue(ctx, rq_json):
    t = rq_json["time"]
    rq_name = rq_json["name"]
    user = ctx.message.author
    embed=discord.Embed(
        title="Your reminder will continue  ✅",
        description="You'll be reminded for ``" + rq_json["name"] + "`` again",
        color=0x00CC66
    )
    embed.set_footer(text=user.name, icon_url=user.avatar_url)
    return embed

async def timer_react(ctx, embed):
    bot = ctx.bot
    reaction = None
    message = await ctx.send("<@!" + str(ctx.message.author.id) + ">", embed=embed)
    rq_continue = False
    rq_json = requests.retrieve_json_id(files.request_dir(), ctx.author.id, ctx.message.id)
    # 5 second grace to ensure it cancels
    t = rq_json["time"] - 5

    for emoji in confirm_control_emoji:
        await message.add_reaction(emoji)

    def check(reaction, user):
        return reaction.message.id == message.id and user == ctx.author

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout = t, check = check)
        if str(reaction) == '✅':
            rq_continue = True
        elif str(reaction) == '❌':
            #await remove_reactions(ctx, message)
            await ctx.send(embed=reminder_cancel(ctx, rq_json))
            requests.remove(files.request_dir(), ctx.message.id, bot.coroutineList)
    except asyncio.TimeoutError:
        requests.remove(files.request_dir(), ctx.message.id, bot.coroutineList)
        await ctx.send(embed=reminder_cancel_timeout(ctx, rq_json))

    if rq_continue:
        await ctx.send(embed=timer_continue(ctx, rq_json))
    await remove_reactions(ctx, message)

def prefix_current(ctx, pfx):
    embed=discord.Embed(
        title="My prefix is ``" + pfx + "`` for this guild",
        description="If you have prefix conflicts, mention me followed by a new prefix!" + 
        "\nOnly single letter prefixes can be applied this way for exception reasons",
        color=0x00CC66
    )
    return embed

def prefix_change(ctx, pfx):
    embed=discord.Embed(
        title="Success!",
        description="Prefix changed to ``" + pfx + "``",
        color=0x00CC66
    )
    return embed

def prefix_dms(ctx):
    embed=discord.Embed(
        title="I have no prefix for DMs!",
        description="Simply send the command keyword like ``help``"
    )
    return embed

def prefix_length(ctx):
    embed=discord.Embed(
        title="That prefix is too long",
        description="Anyhing less than 10 characters is more reasonable c:"
    )
    return embed

async def embed_pages(ctx, pages):
    if len(pages) < 2:
        await ctx.send(embed=pages[0])
        return
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
            try:
                if ctx.guild is not None:
                    await message.remove_reaction(reaction, user)
            except discord.Forbidden:
                pass
        except asyncio.TimeoutError:
            break
    await remove_reactions(ctx, message)

async def remove_reactions(ctx, message):
    try:
        if ctx.guild is not None:
            await message.clear_reactions()
    except discord.Forbidden:
        # replace with smthn formal
        await ctx.send("I don't have permission to remove reactions :(\nPlease make sure I have the ``Manage Message`` permission")