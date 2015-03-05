# infiniteswitch

InfiniteSwitch builds upon InfiniteStop by facilitating transitions between two songs. InfiniteSwitch calculates appropriate transitions between sections within each song and between sections between songs, then chooses sections to play until the playing time reaches the limit provided by the user.

The means by which section distances are determined is detailed in the inquiry report for 3 March. Please note that the distance between keys is not perfected for this module: it treats G as as far away from C as F#, which is not true musically speaking. This discrepancy will be fixed for later modules once the key distances assignment is completed.

In the future, section distances will be lessened by introducing tempo stretching and autotuning; how exactly is the subject for a future report.

The module is executed by providing two mp3 file names along with the number of minutes for which you want the audio to run, like so:
```
python infiniteswitch.py UnderPressure.mp3 IceIceBaby.mp3 5
```