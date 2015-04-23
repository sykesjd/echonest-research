# pypitch

pypitch is a reverse-engineered alternative to the problematic Soundtouch for those wishing to pitch-shift using Echonest Remix.

The pitch shifting is performed using tempo shifting and data resampling. The tempo is stretched or compressed a certain amount, then the number of samples is reduced or increased to bring the tempo back to the original tempo but at a different pitch.

The original plan was to use `scipy.signal.resample` to perform the reduction and increase of samples, but the function proved too inefficient for practical use in this module; a more direct approach is used instead.

pypitch provides two key methods: `shiftPitchSemiTones` and `shiftPitchOctaves`. Both methods are provided with the data for the audio (similar to what is passed to the `dirac.timeScale` method) and the number of semitones/octaves by which to shift the pitch. The method returns the new data, which can then be synthesized into audio using Remix's `audio.AudioData`.

For simplicity's sake, the `shiftPitchSemiTones` method will only shift within ±6 semitones; any number with a greater absolute value will be reduced to within that range by adding or subtracting 12 as necessary. The method is implemented as such to cater to the eventual final product of pitch-shifting between songs: we want the shift to be as small as possible.

A test module `testpypitch.py` is provided as an example of how to use pypitch: it takes in an audio file, shifts the pitch by a user-specified amount, then outputs the result as another audio file.

The test module is executed providing by the audio file name and the number of semitones by which you wish to shift the pitch (negative for shifting down), like so:
```
python testpypitch.py BWV552.mp3 -2
```