import logging
import time
import utils.file_manager as files

def init_logs(path):
    files.make_dir(path)
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=path + time.strftime("%Y-%m-%d-%H%M%S") + '.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger

def exception(ctx, e, logger):
    logger.error("Unhandled exception on: \"" + ctx.message.content + "\" by " + ctx.message.author.name + " (" + str(ctx.message.author.id) + ")")
    if ctx.guild is not None:
        logger.error("Guild: " + ctx.guild.name + " (" + str(ctx.guild.id) + ") ")
        logger.error("Members: " + str(ctx.guild.member_count))
    else:
        logger.error("Occured in DMs")
    logger.error(str(repr(e)))

def log(s, logger):
    logger.info(s)