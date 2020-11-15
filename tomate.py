import select
import sys
import time
import math
import os
import cursor
import subprocess

################################################################################
## This is released under GNU Affero License 3.0
##


## The idea is that the pomodoro app can call hooks by running these commands, leave None to do nothing.
COMMAND_START_WORK = [ "bash", "/home/vx/scripts/tomateevents.sh", "start_work" ]
COMMAND_END_WORK = [ "bash", "/home/vx/scripts/tomateevents.sh", "end_work" ]
COMMAND_START_BREAK = [ "bash", "/home/vx/scripts/tomateevents.sh", "start_break" ]
COMMAND_END_BREAK = [ "bash", "/home/vx/scripts/tomateevents.sh", "end_break" ]

# Every second, update the clock.
INTERVAL_SECONDS = 1.0

# Every 15 seconds, refresh the whole color , to cleanup garbage letters that may have appeared because someone
# pressed some keys in the terminal window...
GARBAGE_CLEANUP = 15

# In the menu, wait 10 seconds before selecting a default option
MENU_WAIT = 10


# ANSI codes that can be customized
RED     = "\u001b[41;1m"
GREEN   = "\u001b[48;5;22m"
RESET   = "\033[0;0m"


# People have different views of how pomodoro should work. I like 25 minutes of
# follower by 5 minutes-long breaks, except that after 4 work pomodoros, there
# is a 15 minute break. But this can be customized. "w" means work, "b" means break
#
CYCLE = [
    ("w", 25),
    ("b",  5),
    ("w", 25),
    ("b",  5),
    ("w", 25),
    ("b",  5),
    ("w", 25),
    ("b", 15),
]

def mode_color(mode):
    if mode == 'w':
        return RED
    elif mode == 'b':
        return GREEN
    else:
        return RESET

def cursor_top():
    # ansi trick to move the output to the top of the terminal
    sys.stdout.write("\033[0;0H")

def line(mode, text):
    # Print a line, with color and centered and everything
    w = os.get_terminal_size().columns
    rem = max(0, w - len(text) )
    left = math.floor( rem / 2 )
    sys.stdout.write( mode_color(mode) + ' ' * left + text )
    sys.stdout.flush()


def v_center():
    cursor_top()
    # center the output vertically.
    h = os.get_terminal_size().lines
    y = math.floor( (h-1) / 2)
    for i in range(y):
        print("")
    sys.stdout.write("\r")
                      
def format(s):
    s = math.floor(s + 0.5)
    m = s / 60
    s = s % 60
    return "%02d:%02d" % (m, s)

def clear(mode):
    # clear the whole screen, paint it the color you want
    cursor_top()
    siz = os.get_terminal_size()
    w = siz.columns
    h = siz.lines
    c = mode_color(mode)
    for i in range(h):
        print( c + " "*w )
    cursor_top()

def exhaust():
    # This is a tricky one. We don't want previous keystrokes to be read
    # when using input() when we want to prompt for an enter key. So this
    # will ensure to exhaust any pending stdin content before prompting.
    while True:
        i, o, e = select.select( [sys.stdin], [], [], 0.1 )
        if i:
            sys.stdin.readline()
        else:
            break

def send_event(mode, start):
    # Run the hook commands, if any
    if start:
        command = COMMAND_START_BREAK if mode == 'b' else COMMAND_START_WORK
    else:
        command = COMMAND_END_BREAK if mode == 'b' else COMMAND_END_WORK
    if command != None:
        subprocess.Popen(command, stdout=None)

def menu():
    # At the beginning, display the options to ask which timer to show first
    # it's a mess of a hieroglyphic stuff because I wanted the terminal window
    # to be compact, should be easy to change it to something more verbose.
    #
    # grab a list of unique options from the CYCLE array and their indexes
    OPTIONS= []
    seen = set()
    for i in range( len(CYCLE) ):
        x = CYCLE[i]
        if not x in seen:
            seen.add(x)
            OPTIONS.append(i)
    clear('n')
    # print it, wrap the text
    w = os.get_terminal_size().columns
    p = 0
    for i in range( len(OPTIONS) ):
        x = CYCLE[ OPTIONS[i] ]
        s = "%d=%s%d " % (i+1, x[0], x[1])
        if p + len(s) > w:
            sys.stdout.write("\n")
            p = 0
        p += len(s)
        sys.stdout.write(s)


    current = 0
    cursor.show()
    try:
        i, o, e = select.select( [sys.stdin], [], [], MENU_WAIT )
    except KeyboardInterrupt:
        return -1, False
    stop = True
    if i:
        stop = False
        o = int( sys.stdin.readline().strip() ) - 1
        if o == -1:
            cursor_top()
            clear('n')
            line("n","00:00")
            exhaust()
            input()
            menu()
            return


        current = OPTIONS[o]
    return (current, stop)


def loop():
    (current, stop) = menu()
    cursor.hide()
    while True:
        if current == -1:
            # someone pressed ctrl+C during the menu, that's our exit cue
            print(".")
            return
        try:
            mode= CYCLE[ current ][0]

            clear(mode)
            m = CYCLE[ current ][1] * 60
            if stop:
                # wait for user to press enter
                cursor_top()
                v_center()
                line(mode, format(m) )
                exhaust()
                cursor.show()
                input()
                clear(mode)

            cursor.hide()
            t0 = time.time()
            t1 = t0 + m
            r = 0
            send_event(mode, True)

            while time.time() < t1:
                diff = t1 - time.time()
                cursor_top()
                # some keystrokes leave garbage in the terminal, this cleans it up every 15 cycles
                r += 1
                if r >= GARBAGE_CLEANUP:
                    clear(mode)
                    r = 0
                v_center()
                line(mode, format(diff) )
                time.sleep( min(INTERVAL_SECONDS, diff) )
            send_event(mode, False)

            current = (current + 1) % len(CYCLE)
            stop = True
        except KeyboardInterrupt:
            #allow to restart the menu by using ctrl + c
            (current, stop) = menu()

loop()