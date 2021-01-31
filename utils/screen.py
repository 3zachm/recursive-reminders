import asyncio
import curses
import discord

stdscr = curses.initscr()

def print_counts(bot):
    stdscr.addstr(0, 0, "Guilds: " + str(len(bot.guilds)))
    stdscr.addstr(1, 0, "Requests: " + str(len(bot.coroutineList)))

    stdscr.refresh()

async def main(bot):
    print_counts(bot)
    # scuffed, should make a thread later instead
    # side-effect of up to 5s wait for exit
    await asyncio.sleep(5)
    curses.curs_set(0)
    #curses.cbreak()
    stdscr.nodelay(True)
    await check_interrupt(stdscr)

async def loop(bot):
    while True:
        await main(bot)

async def check_interrupt(stdscr):
    try:
        h = stdscr.getch()
        if h == 3:
            raise KeyboardInterrupt
        if h == 26:
            raise EOFError
    except KeyboardInterrupt:
        quit()