#!/usr/bin/env python
# encoding: utf=8
"""
sarabande.py

Digest only the second beat of every bar and place rubato on second of every three beats.

By Jesse David Sykes, 2015-02-10
Based on one.py by Ben Lacker, 2009-02-18, with additional code from simple_stretch.py by Thor Kell, 2013-11-18.
"""
import echonest.remix.audio as audio
import dirac

usage = """
Usage: 
    python sarabande.py <input_filename> <output_filename>

Example:
    python sarabande.py TwoForOne.mp3 ReallyTwoForOne.mp3
"""

def main(input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    bars = audiofile.analysis.bars
    collect = audio.AudioQuantumList()
    count = 0
    for bar in bars:
		try:
			beat = bar.children()[1]
			beat_audio = beat.render()
			scaled_beat = dirac.timeScale(beat_audio.data, 1.2) if count == 1 else dirac.timeScale(beat_audio.data, 1.0)
			ts = audio.AudioData(ndarray=scaled_beat, shape=scaled_beat.shape, sampleRate=audiofile.sampleRate, numChannels=scaled_beat.shape[1])
			collect.append(ts)
			count = (count + 1) % 3
		except IndexError:
		    pass
    out = audio.assemble(collect, numChannels=2)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)
