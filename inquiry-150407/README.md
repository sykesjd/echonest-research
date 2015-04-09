# Problem
SoundTouch, the module with which Remix is supposed to be able to change the pitch of an audio quantum, has been providing problems for everyone in class trying to use it. Is there a way to reverse engineer another means of pitch shifting without SoundTouch?

# Questions
1. How does one pitch shift using tempo shifting?
2. How does Remix perform tempo shifting?
3. What else does Remix provide to aid in pitch shifting aside from tempo shifting?

# Resources

1. Personal communication with Dr. Parry
2. [Cycle-Dirac Remix Example]
3. [SciPy Resample Documentation]

### 1. Mini-abstract and relevance of personal communication with Dr. Parry

When in Dr. Parry's office trying to beat SoundTouch into submission, I offhandly expressed the idea of reverse engineering SoundTouch myself - which he, thankfully for the reader of this report, took seriously.

Dr. Parry told me how to pitch shift up an octave using tempo shifting: one would halve the tempo of the audio, providing twice as many frames of audio, then select every other sample for a new set of audio data. For going down an octave, you would do it the other way around: select every other sample, then halve the tempo.

The process of pitch shifting can therefore be recreated with two functions: a tempo shifting function and a sample selection function. How much the tempo is shifted and which sample are selected will depend on how much we want to shift the pitch.

### 2. Mini-abstract and relevance of [Cycle-Dirac Remix Example]

The first function necessary for pitch shifting is tempo shifting. As shown in a previous inquiry report, the following code shows us how Remix performs tempo shifting with Dirac:

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

The method we want is `dirac.timeScale`. The method is passed the set of audio data for an audio quantum - a numpy array - and a ratio for how to stretch the tempo, where a ratio greater than 1 *decreases* the tempo and a ratio less than 1 *increases* the tempo (I was incorrect in the last inquiry report on this). The method returns another set of audio data (i.e. another numpy array), which is then passed into `audio.audioData` to synthesize as an AudioQuantum.

### 3. Mini-abstract and relevance of [SciPy Resample Documentation]

The second function necessary for pitch shifting is sample selection. This function is provided by `scipy.signal.resample(x,num)`, where `x` is the data array and `num` is the number of samples in the resulting data array.

Using this function, we can select samples from the numpy array of data and place them into another numpy array, which we can then synthesize into AudioData and pass into the new aqplayer. I will be building such a function for my next research module.

[Cycle-Dirac Remix Example]: https://github.com/echonest/remix/blob/master/examples/stretch/cycle_dirac.py
[SciPy Resample Documentation]: http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample.html