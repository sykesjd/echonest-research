# Problem
We want to be able to change a section's tempo and key to match another's.

# Questions
1. How does Remix change the pitch of an audio quantum?
2. How does Remix change the tempo of an audio quantum?
3. How does the section similarity calculation change based on these changes?

# Resources

1. [BeatShift Remix Example]
2. [Cycle-Soundtouch Remix Example]
3. [Cycle-Dirac Remix Example]

### 1. Mini-abstract and relevance of [BeatShift Remix Example]

The Remix API docs fail to succinctly detail how to shift tempo and pitch, so we are left to viewing Remix examples to see how it's done. beatshift.py takes all the beats in a track and shifts the pitch of each consecutive beat one semitone lower than the last, resetting after every octave. The relevant code is below:

```python
from echonest.remix import audio, modify

for i, beat in enumerate(beats):
    data = audiofile[beat].data
    number = beat.local_context()[0] % 12
    new_beat = soundtouch.shiftPitchSemiTones(audiofile[beat], number*-1)
    out_data.append(new_beat)
```

The above code takes a beat, determines the number of the beat and mods it by 12 (an octave), then shifts the pitch by that number down using the `soundtouch.shiftPitchSemiTones` method. The method is passed an AudioQuantum and an integer value for how much to shift the pitch, and returns a new AudioQuantum. The new quantum is then appended to the array of quanta to be played. This method provides the answer to question 1.

### 2. Mini-abstract and relevance of [Cycle-Soundtouch Remix Example]

In addition to shifting pitch, the Soundtouch API in Remix also allows for shifting tempo. However, in the cycle_soundtouch Remix example, the documentation includes this tidbit:

> Currently there is a bug with soundtouch. Please see cycle_dirac, and use dirac for time stretching.

No further details are given, but we will nonetheless trust the hand that feeds us and visit the cycle_dirac example.

### 3. Mini-abstract and relevance of [Cycle-Dirac Remix Example]

The cycle_dirac Remix example takes each bar in the and time compresses or stretches each beat in the bar by an amount dependent on the bar number and beat number. The relevant code is below:

```python
for bar in bars:
    bar_ratio = (bars.index(bar) % 4) / 2.0
    beats = bar.children()
    for beat in beats:
        beat_index = beat.local_context()[0]
        ratio = beat_index / 2.0 + 0.5
        ratio = ratio + bar_ratio # dirac can't compress by less than 0.5!
        beat_audio = beat.render()
        scaled_beat = dirac.timeScale(beat_audio.data, ratio)
        ts = audio.AudioData(ndarray=scaled_beat, shape=scaled_beat.shape, 
                             sampleRate=audiofile.sampleRate, numChannels=scaled_beat.shape[1])
        collect.append(ts)
```

The method we want is `dirac.timeScale`. The method is passed the set of audio data for an audio quantum and a ratio for how to stretch the tempo, where a ratio greater than 1 increases the tempo and a ratio less than 1 decreases the tempo. The method returns another set of audio data, which is then passed into `audio.audioData` to synthesize as an AudioQuantum. This method provides the answer to question 2.

### Discussion

Allowing for the shifting of pitch and tempo for a section will increase the number of possible transitions from a section. The following aspects of the section similarity calculation will be changed:
* Tempo: the differences in tempo will become less important, though still part of the calculation - a weight of 1 instead of 10, in Infinite Jukebox terms. Incidentally, the calculation will need to account for the tempi of two sections being integer multiples of each other or close to such, which will require a relatively dense set of calculations that needs to take into account whether the meter is simple or compound. Those calculations will be the topic of another inquiry.
* Key: differences in key will likewise become less important - a weight of 10 instead of 100. The distance between keys will have to be calculated as a torus distance, with a sign indicating up or down in direction.
* Pitches: the distance between the pitch vectors for the first segment of each section will need to be modified to account for a possible difference in keys. The question to ask would be which value is smaller: the distance between the pitch vectors as is, or the distance between the pitch vector of the first and the pitch vector of the second shifted on account of the key difference. If the first is smaller, then it will be unnecessary to change the key of the second section if it becomes a possibility for an edge.

[BeatShift Remix Example]: https://github.com/echonest/remix/blob/master/examples/stretch/beatshift.py
[Cycle-Soundtouch Remix Example]: https://github.com/echonest/remix/blob/master/examples/stretch/cycle_soundtouch.py
[Cycle-Dirac Remix Example]: https://github.com/echonest/remix/blob/master/examples/stretch/cycle_dirac.py