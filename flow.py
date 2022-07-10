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

# FLOWTIME

## The idea is that the pomodoro app can call hooks by running these commands, leave None to do nothing.
COMMAND_START_WORK = [ "bash", "/home/vx/scripts/flowevents.sh", "start_work" ]
COMMAND_END_WORK = [ "bash", "/home/vx/scripts/flowevents.sh", "end_work" ]
COMMAND_START_BREAK = [ "bash", "/home/vx/scripts/flowevents.sh", "start_break" ]
COMMAND_END_BREAK = [ "bash", "/home/vx/scripts/flowevents.sh", "end_break" ]

# This is the important part, how to calculate the break time given a work
# time? The whole following formula is based on my own Heuristics
# you might want to tweak it, or maybe use a simple approach?
def calculate_break_time(total_worked):
    return total_worked * ( 0.2 + total_worked / 19000.0 )

# Every second, update the clock.
INTERVAL_SECONDS = 1.0

MAX_WORK_SECONDS = 60 * 60


# Every 15 seconds, refresh the whole color , to cleanup garbage letters that may have appeared because someone
# pressed some keys in the terminal window...
GARBAGE_CLEANUP = 15

# ANSI codes that can be customized
RED     = "\u001b[41;1m"
GREEN   = "\u001b[48;5;22m"
RESET   = "\033[0;0m"


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
    s = math.floor(s)
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

def clear_if_needed_creator():
    t0 = time.time()
    last_update = [time.time() - GARBAGE_CLEANUP]

    def closure(mode):
        t = time.time()
        if t - last_update[0] >= GARBAGE_CLEANUP:
            last_update[0] = t
            clear(mode)

    return closure


clear_if_needed = clear_if_needed_creator()

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

def wait_for_enter(duration):
    # return true if enter was pressed, false if duration ended without an enter
    i, o, e = select.select( [sys.stdin], [], [] , INTERVAL_SECONDS )
    return True if i else False

def prompt(mode):
    clear(mode)

    exhaust()
    while True:
        clear_if_needed(mode)
        cursor_top()
        v_center()
        line( mode, format(0.00) )
        cursor.show()
        if wait_for_enter(INTERVAL_SECONDS):
            break



def work_time():
    send_event('w', True)
    t0 = time.time()

    def get_delta() :
        return min( time.time() - t0, MAX_WORK_SECONDS )

    clear("w")
    exhaust()
    while True:
        delta = get_delta()

        clear_if_needed("w")

        cursor_top()
        v_center()
        line( "w", format(delta) )

        rem = INTERVAL_SECONDS* math.floor(delta/INTERVAL_SECONDS) + INTERVAL_SECONDS - delta
        if rem >= INTERVAL_SECONDS:
            rem = 0.001
        if wait_for_enter(rem):
            break
    
    send_event('w', False)
    
    return get_delta()

def break_time(duration):
    send_event('b', True)
    clear("b")

    t1 = time.time() + duration
    while t1 - time.time() > 0 :
        clear_if_needed("b")
        cursor_top()
        v_center()
        line( "b", format(t1 - time.time() ) )
        time.sleep(INTERVAL_SECONDS)
    send_event('b', False)

def loop():
    stop = False
    prompt("n")
    while True:
        cursor.hide()
        total_worked = work_time()
        break_time( calculate_break_time(total_worked) )
        prompt("w")

try:
    loop()
except KeyboardInterrupt:
    clear("n")
    print(".")
    cursor.show()

