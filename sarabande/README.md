# sarabande

In classical music, a sarabande is a slow waltz where the emphasis is placed on the second beat of the measure, usually by the use of rubato.

This module takes the sarabande concept to the extreme: given an input mp3 file, it will digest the second beat of every measure in the song, place rubato on the second of every three digested beats, and return the result as an mp3.

The module is executed like so:
```
python sarabande.py NameOfFile.mp3
```