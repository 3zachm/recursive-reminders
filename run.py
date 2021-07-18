import discord
import configparser
import os
import io
import asyncio
import json
import atexit
import time
from discord.errors import Forbidden
from discord.ext import commands
import utils.embed_generator as embeds
import utils.file_manager as files
import utils.log_manager as logs
import utils.request_manager as requests
import utils.commands as cmds
import utils.screen as screen
import utils.eval as evalu
import utils.utils as utils

boot_time = time.time()
config = configparser.ConfigParser()
files.script_dir = os.path.dirname(os.path.realpath(__file__))
files.delete_contents(files.request_dir())

# generate empty config files
files.make_config(files.config_loc())
files.make_prefixes(files.prefix_loc())
files.make_dir(files.request_dir())

# open config file
with open(files.config_loc()) as c:
    discord_config = c.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_file(io.StringIO(discord_config))

try:
    default_prefix = config.get('discord', 'default_prefix')
    generate_logs = config.getboolean('python', 'generate_logs')
    bot_token = config.get('discord', 'token')
    tmp_screen = config.getboolean('python', 'enable_curses')
    enable_eval = config.getboolean('python', 'enable_eval')
except (configparser.NoSectionError, configparser.NoOptionError) as e:
    print(e)
    print("Ensure config file has all entries present. If you recently pulled an update, consider regenerating the config")
    quit()

#logging
if generate_logs:
    logger = logs.init_logs(files.logs_dir())

# initializes a server in the prefix file
def initPrefix(serverID):
    with open(files.prefix_loc(), 'r') as r:
        prefixes = json.load(r)
    prefixes[str(serverID)] = default_prefix
    with open(files.prefix_loc(), 'w') as w:
        json.dump(prefixes, w, indent=4)

def get_prefix(bot, message):
    if not message.guild:
        return ""
    with open(files.prefix_loc(), 'r') as r:
        prefixes = json.load(r)
    try:
        pfx = prefixes[str(message.guild.id)]
    except KeyError:
        initPrefix(message.guild.id)
        with open(files.prefix_loc(), 'r') as r:
            prefixes = json.load(r)
        pfx = prefixes[str(message.guild.id)]
    return pfx

bot = commands.Bot(command_prefix = get_prefix)
bot.remove_command('help')
bot.coroutineList = []
bot.reset_warning = False
use_screen = tmp_screen

@bot.event
async def on_ready():
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    # generate bot owner
    files.make_owners(files.owners_loc(), bot)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="booting..."))
    # start periodic presence update
    bot.presence_routine = asyncio.create_task(update_presence())
    if use_screen:
        asyncio.create_task(screen.loop(bot))
    else:
        print("Screen disabled\n\nRunning...")

@bot.event
async def on_guild_join(guild):
    initPrefix(guild.id)
    if generate_logs:
        logs.log("Joined \"" + guild.name + "\" - " + str(guild.id), logger)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    if isinstance(error, commands.errors.CheckFailure):
        return
    if isinstance(error, commands.errors.MissingPermissions) and ctx.guild is None:
        return
    if isinstance(error, commands.errors.MissingRequiredArgument):
        if str(ctx.command) == "reminder add":
            await ctx.send(embed=embeds.reminder_add_missing(ctx, guild_prefix(ctx), bot))
            return
        if str(ctx.command) == "reminder stop":
            if len(requests.retrieve_list(ctx.author.id, files.request_dir())) == 1:
                await reminder_stop(ctx, 1)
                return
            await ctx.send(embed=embeds.reminder_stop_missing(ctx, guild_prefix(ctx), bot))
            return
        if str(ctx.command) == "reminder move":
            if len(requests.retrieve_list(ctx.author.id, files.request_dir())) == 1:
                await reminder_move(ctx, 1)
                return
            await ctx.send(embed=embeds.reminder_move_missing(ctx, guild_prefix(ctx), bot))
            return
    # unhandled exception occurred
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(embed=embeds.unhandled(ctx, error))
    if generate_logs:
        logs.exception(ctx, error, logger)
    else:
        raise error

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    msg = message.content
    if ctx.guild is None and (message.content.startswith('!') or message.content.startswith('.')):
        await ctx.send("I am prefix-less in DMs! Simply type the command like `help`")
    if bot.user.mentioned_in(message):
        if message.mention_everyone:
            return
        if message.mentions[0] == bot.user:
            # get first mention value up to a space
            try:
                first_mention = msg[0 : msg.index(' ')]
            except ValueError:
                first_mention = ''
            if ctx.guild is None:
                embed = embeds.prefix_dms(ctx)
                await ctx.send(embed=embed)
            # if mention is first and has a space after it
            elif first_mention == (f'<@!{bot.user.id}>') and ctx.message.author.guild_permissions.administrator:
                index = msg.index(' ')
                await prefix(ctx, msg[index + 1 : index + 2]) # i'm bad at python?
            else:
                pfx = str(get_prefix(bot=bot, message=message))
                if pfx == '':
                    pfx = 'None'
                embed = embeds.prefix_current(ctx, guild_prefix(ctx))
                await ctx.send(embed=embed)
    await bot.process_commands(message)

@bot.command(name="help", help=cmds.help_help, description=cmds.help_args)
async def help(ctx):
    await embeds.help(ctx, guild_prefix(ctx), bot)

@bot.command(name="owners", help=cmds.owners_help, description=cmds.owners_args)
async def owners(ctx):
    await ctx.send(embed=embeds.owners(ctx))

@bot.group(name="system", aliases=["sys"], invoke_without_command=True)
@commands.check(cmds.owner_check)
async def system(ctx):
    pass

@system.command(name="pt")
async def system_pt(ctx):
    if cmds.owner_check(ctx):
        await ctx.send("You have owner permissions.")

@system.command(name="fstop")
@commands.check(cmds.owner_check)
async def system_fstop(ctx, rq_ID):
    requests.remove(files.request_dir(), int(rq_ID), bot.coroutineList)
    await ctx.send("Successfully stopped.")

@system.command(name="global_dm")
@commands.check(cmds.owner_check)
async def system_global_dm(ctx, *, dm_msg):
    bot.reset_warning = True
    bot.presence_routine.cancel()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="reseting soon!"))
    rqs = files.get_json_userids(files.request_dir())
    embed = embeds.global_dm_message(ctx, dm_msg)
    for uid in rqs:
        user = await bot.fetch_user(uid)
        try:
            await user.send(embed=embed)
        except Forbidden:
            pass

# modified from Copyright (c) 2021 beeracademy (https://github.com/beeracademy/discord-bot)
# thank you for being smarter than me <3
@system.command(name="evaluate", aliases=["eval"])
@commands.check(cmds.eval_check)
async def evaluate(ctx, *, stmts):
    if ctx.message.author.id != 106188449643544576: # im checking twice idc
        return
    stmts = stmts.strip().replace("```python", "```").strip("`")
    # not like the filesystem or uptime of my pi matters much anyways, would be more concerned about my account
    exit_str = ["/", "\\", "..", "5c", "2f", "2e", "bot_token"]
    if any(exit_strs in stmts for exit_strs in exit_str):
        await ctx.send("```Direct file operation-related characters not allowed```")
        return

    if not stmts:
        await ctx.send("After stripping `'s, stmts can't be empty.")
        return

    res = await evalu.eval_stmts(stmts, {"bot": bot, "ctx": ctx})
    escaped = evalu.code_block_escape(repr(res))
    message = f"```python\n{escaped}\n```"
    if len(message) > 2000:
        prefix = "Truncated result to length 0000:\n"
        suffix = "\n```"
        message = message.rstrip("`").strip()

        new_length = 2000 - len(prefix) - len(suffix)
        prefix = prefix.replace("0000", str(new_length))
        message = prefix + message[:new_length] + suffix

    await ctx.send(message)

@bot.command(name="uptime", help=cmds.uptime_help, description=cmds.uptime_args)
async def uptime(ctx):
    await ctx.send("**Uptime**: `{0}`\n**Server**: `{1}`".format(utils.get_uptime(boot_time), utils.get_sysuptime()))

@bot.command(name="ping", aliases=["test"], help=cmds.ping_help, description=cmds.ping_args)
async def ping(ctx):
    latency = bot.latency*1000
    sent_time = ctx.message.created_at
    botmsg = await ctx.send("**Response Latency**: `{0}ms`\n**Discord Latency**: ".format(round(latency, 0)))
    botmsg_time = botmsg.created_at
    msg_time = float((botmsg_time - sent_time).total_seconds()*1000)
    await botmsg.edit(content=botmsg.content + " `{0}ms`".format(round(msg_time, 0)))

@bot.command(name="prefix", help=cmds.prefix_help, description=cmds.prefix_args)
@commands.has_permissions(administrator=True)
async def prefix(ctx, prefix=None):
    if prefix is None:
        embed = embeds.prefix_current(ctx, guild_prefix(ctx))
    elif len(prefix) > 10:
        embed = embeds.prefix_length(ctx)
    else:
        with open(files.prefix_loc(), 'r') as r:
            prefixes = json.load(r)
        prefixes[str(ctx.guild.id)] = prefix
        with open(files.prefix_loc(), 'w') as w:
            json.dump(prefixes, w, indent=4)
        if prefix == '':
            prefix = 'None'
        embed = embeds.prefix_change(ctx, prefix)
    await ctx.send(embed=embed)

@bot.command(name="invite", help=cmds.invite_help, description=cmds.invite_args)
async def invite(ctx):
    await ctx.send(embed=embeds.invite_link(ctx))

@bot.group(name="reminder", aliases=["r"], invoke_without_command=True, help=cmds.reminder_help, description=cmds.reminder_args)
async def reminder(ctx):
    embed = embeds.reminder_base(ctx, guild_prefix(ctx), bot)
    await ctx.send(embed=embed)

@reminder.command(name="add", aliases=["create"], help=cmds.reminder_add_help, description=cmds.reminder_add_args)
async def reminder_add(ctx, t, *, rqname):
    try:
        t = int(t)
    except ValueError:
        await ctx.send("That time doesn't seem like a real integer. Decimals aren't supported at the moment.")
        return
    if len(rqname) > 50:
        embed = embeds.request_length(ctx, "reminder name", "50 characters")
        await ctx.send(embed=embed)
    elif t > 720: #currently in minutes
        embed = embeds.request_length(ctx, "time", "12 hours")
        await ctx.send(embed=embed)
    elif t == 0:
        await ctx.send("You don't need a 0 minute timer :)")
    elif t < 0:
        await ctx.send("Counting by negatives seems dangerous")
    elif len(requests.retrieve_list(ctx.author.id, files.request_dir())) > 9:
        embed = embeds.reminder_list_length(ctx)
        await ctx.send(embed=embed)
    else:
        t = int(t) * 60
        rq_json = requests.create(ctx, files.request_dir(), rqname, t)
        embed = embeds.reminder_set(ctx, guild_prefix(ctx), t, rqname)
        await ctx.send(embed=embed)
        if bot.reset_warning:
            await ctx.send("**Please note that a reset is expected to happen soon! Don't rely on this timer for the next hour or so**" +
            "\nThe bot's presence will return to normal when it's been reset")
        timer_task = asyncio.create_task(timer(ctx, rq_json), name=ctx.message.id)
        bot.coroutineList.append([ctx.message.id, timer_task])

@reminder.command(name="list", help=cmds.reminder_list_help, description=cmds.reminder_list_args)
async def reminder_list(ctx):
    requests_list = requests.retrieve_list(ctx.message.author.id, files.request_dir())
    await embeds.reminder_list(ctx, requests_list)

@reminder.command(name="stop", aliases=["remove"], help=cmds.reminder_stop_help, description=cmds.reminder_stop_args)
async def reminder_stop(ctx, request):
    user = ctx.message.author
    try:
        request = int(request)
    except ValueError:
        try:
            if str(request) == "all":
                rq_list = requests.retrieve_list(ctx.message.author.id, files.request_dir())
                if len(rq_list) < 1:
                    await ctx.send(embed=embeds.reminder_none(ctx, guild_prefix(ctx)))
                    return
                for rq in rq_list:
                    requests.remove(files.request_dir(), rq['request'], bot.coroutineList)
                await ctx.send(embed=embeds.reminder_cancel_all(ctx))
                return
        except ValueError:
            pass
        await ctx.send(embed=embeds.reminder_stop_missing(ctx, guild_prefix(ctx), bot))
        return

    if requests.retrieve_list(user.id, files.request_dir()) == []:
        embed=embeds.reminder_none(ctx, guild_prefix(ctx))
    else:
        try:
            rq_json = requests.retrieve_json(user.id, files.request_dir(), request)
            requests.remove(files.request_dir(), rq_json['request'], bot.coroutineList)
            embed = embeds.reminder_cancel(ctx, rq_json)
        except IndexError:
            embed = embeds.reminder_cancel_index(ctx, guild_prefix(ctx), request)
    await ctx.send(embed=embed)

@reminder.command(name="move", help=cmds.reminder_move_help, description=cmds.reminder_move_args)
async def reminder_move(ctx, request):
    try:
        request = int(request)
    except ValueError:
        await ctx.send(embed=embeds.reminder_move_missing(ctx))
        return
    try:
        rq_json = requests.retrieve_json(ctx.author.id, files.request_dir(), request)
        if ctx.guild is None:
            channel = 1
            guild = ""
        else:
            channel = ctx.channel.id
            guild = ctx.guild.name
        requests.edit_json_val(rq_json['user'], files.request_dir(), rq_json['request'], 'channel', channel)
        requests.edit_json_val(rq_json['user'], files.request_dir(), rq_json['request'], 'source', ctx.message.id)
        rq_new_json = requests.edit_json_val(rq_json['user'], files.request_dir(), rq_json['request'], 'guild', guild)
        await ctx.send(embed=embeds.reminder_move_success(ctx, rq_new_json))
    except IndexError:
        await ctx.send(embed=embeds.reminder_cancel_index(ctx, guild_prefix(ctx), request))

@reminder.command(name="wait", help=cmds.reminder_wait_help, description=cmds.reminder_wait_args)
async def reminder_wait(ctx, request = 1):
    try:
        request = int(request)
    except ValueError:
        await ctx.send(embed=embeds.reminder_wait_missing(ctx))
        return
    try:
        rq_json = requests.retrieve_json(ctx.author.id, files.request_dir(), request)
        if rq_json['wait'] == True:
            rq_new_json = requests.edit_json_val(rq_json['user'], files.request_dir(), rq_json['request'], 'wait', False)
            embed = embeds.reminder_wait_on(ctx, rq_new_json)
        else:
            rq_new_json = requests.edit_json_val(rq_json['user'], files.request_dir(), rq_json['request'], 'wait', True)
            embed = embeds.reminder_wait_off(ctx, rq_new_json)
        await ctx.send(embed=embed)
    except IndexError:
        await ctx.send(embed=embeds.reminder_cancel_index(ctx, guild_prefix(ctx), request))

async def timer(ctx, rq_json):
    t = rq_json["time"]
    react = None
    while(True):
        await asyncio.sleep(t)
        rq_json = requests.retrieve_json_id(files.request_dir(), ctx.author.id, rq_json['request'])
        if rq_json["wait"] == True:
            await asyncio.sleep(rq_json["added"])
        if react is not None:
            react.cancel()
        react = asyncio.create_task(embeds.timer_end(ctx, guild_prefix(ctx), rq_json))

async def update_presence():
    while(True):
        await asyncio.sleep(120)
        rqs_len = len(bot.coroutineList)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=str(rqs_len) + " reminders"))

# offhand because discord.py needs get_prefix to have args
def guild_prefix(ctx):
    return get_prefix(bot=bot, message=ctx.message)

bot.run(bot_token)
atexit.register(files.delete_contents, files.request_dir())