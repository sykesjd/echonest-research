# infinitestop

Infinite Jukebox determines what transitions to take in realtime because it runs under the assumption that it will be playing for essentially forever. Suppose, however, that we want to be playing transitioning music for a predetermined amount of time (the running time of a workout session, for example).

InfiniteStop takes the 60's hit "For What It's Worth" by Buffalo Springfield (known for its chorus starting with "Stop!"), calculates appropriate transitions between sections (instead of beats; see inquiry report for 17 Feb), and, given an amount of time to play from the user, chooses sections to play ahead of time until the time limit is reached, then plays the chosen sections.

The list of sections to play is appended with tatums playing the word "Stop!" at the end for a humorous conclusion.

This method of predetermining transitions can theoretically be extended to a set of multiple songs in the future.

The module is executed by providing the number of minutes for which you want the audio to run, like so:
```
python infinitestop.py 5
```