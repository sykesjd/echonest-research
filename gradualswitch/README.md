# gradualswitch

GradualSwitch provides a look into how to transition between two songs of different tempi. GradualSwitch plays the first section of the first song and the last section of the last song, and transitions between them by altering the tempo of the last few beats of the first section step by step to gradually change from the first tempo to the second.

This method uses Luke Stack's aqplayer to play audio files. The method requires that an intermediary mp3 file be created, due to weaknesses in aqplayer. Perhaps in the future, aqplayer can be updated to incorporate tempo and pitch shifting in a more streamlined manner.

I attempted to add pitch shifting to this module, but SoundTouch so far has refused to work.

The module is executed by providing two mp3 file names, like so:
```
python gradualswitch.py BWV552.mp3 BWV522.mp3
```