import curses
from multiprocessing import connection as mc

ADDRESS = "localhost", 1234


def main(window):

    # window.timeout(-1)
    curses.noecho()
    print(f"connect to {ADDRESS}")
    connection = mc.Listener(ADDRESS).accept()
    window.addstr(0, 0, "ready")
    while True:
        c = window.getch()
        if c == ord("q"):
            window.addstr(0, 0, "q pressed")
            connection.send("q")
            break
        if c == ord("w"):
            window.addstr(0, 0, "w pressed")
            connection.send("w")
        if c == ord("e"):
            window.addstr(0, 0, "e pressed")
            connection.send("e")
        if c == ord("r"):
            window.addstr(0, 0, "r pressed")
            connection.send("r")
        window.addstr(1, 0, connection.recv())
        window.refresh()


curses.wrapper(main)
