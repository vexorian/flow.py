# tomate.py

![Screenshot*](screen.png)

A quick python script I made i, like 4 pomodoros. I've been having issues incorporating Pomodoro into my workflows. Until now I was using a web application but I had some needs that could only be covered by making this script.

* I want the timer to always be visible on the screen.
* Even at two monitors, screen real space is limited for me, so I don't want the timer to use too much space.
* Can't use indicators because I am not sure anymore if I will stick to my current Desktop UI in the long term (Canonical and GNOME keep making Unity less and less viable).
* Web applications are portable but web browsers have too large a footprint and they also use too much space.
* I need to be able to run special hooks when the breaks/work start/end.

At the end, writing a pomodoro terminal script seemed like my best chance. I found it useful for it to color the whole terminal green or red depending on the timer in use. Once the command runs, you only need simple key presses like numbers, enter or ctrl+c to control the timer. You can configure it to run specialized commands when timers start or end. Additionally, I like having as little dependencies as possible running in my host computer,and python3 and a terminal app are some of the few things I can expect to have around regardless of what setup I am using. These are reasons why I couldn't just use the existing terminal pomodoro apps.

As an example, I use the command hooks to make notifications appear in my desktops. You could do things like playing sounds, or making your phone ring. Anything that you can trigger from running a command in your computer is possible.

## Requirements

* It's likely this doesn't work in windows or OS/X
* `pip3 install cursor`


## Usage

Edit tomate.py, tweak the constants to your liking. Specially the constants that determine the commands to run. By editing the constants you can even configure the length of the timers and the specific sequence you want to use.

```
cd path/to/tomate.py
python3 tomate.py
```

A menu appears, press 1, 2 or 3 for the kind of timer you want to start with. The menu is very hard to understand, but that's because I wanted it to be as compact as possible.

Press ctrl+C to cancel the current timer and pick another one.

When the timer finishes, press enter to start the next timer in the cycle.

## Note

I am just sharing the script. I don't intend this to become a real command or app. But I guess nothing stops you from forking it into it (aside of the GPLv3's terms)