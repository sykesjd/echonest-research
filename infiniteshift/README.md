# infiniteshift

InfiniteShift combines previously explored concepts of section distance, tempo shifting, and pitch shifting into one module.

Provide InfiniteShift three audio files and a desired duration of play in minutes, and InfiniteShift will play sections from the three songs in an order determined by which sections make a good transition, shifting the pitch and tempo as necessary to make transitions smoother.

This module uses Luke Stack's aqplayer, modified to include a function for both tempo and pitch shifting before playing. aqplayer in turn uses dirac and pypitch for tempo and pitch shifting.

The module is executed by providing the three audio file names and the desired duration of play in minutes, like so:

```
python infiniteshift.py BWV522.mp3 BWV552.mp3 BWV525.mp3 5
```