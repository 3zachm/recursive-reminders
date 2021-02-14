import asyncio
import curses

def print_counts(bot):
    bot.stdscr.addstr(0, 0, "Guilds: " + str(len(bot.guilds)))
    bot.stdscr.addstr(1, 0, "Requests: " + str(len(bot.coroutineList)))

    bot.stdscr.refresh()

async def main(bot):
    print_counts(bot)
    # scuffed, should make a thread later instead
    # side-effect of up to 5s wait for exit
    await asyncio.sleep(5)
    curses.curs_set(0)
    #curses.cbreak()
    bot.stdscr.nodelay(True)
    await check_interrupt(bot)

async def check_interrupt(bot):
    try:
        h = bot.stdscr.getch()
        if h == 3:
            raise KeyboardInterrupt
        if h == 26:
            raise EOFError
    except KeyboardInterrupt:
        curses.nocbreak()
        curses.endwin()
        quit()

async def loop(bot):
    bot.stdscr = curses.initscr()
    while True:
        await main(bot)