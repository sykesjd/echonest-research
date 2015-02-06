#!/usr/bin/env python
# encoding: utf=8
"""
sarabande.py

Digest only the second beat of every bar.

By Jesse David Sykes, 2015-02-06, based on one.py by Ben Lacker, 2009-02-18.
"""
import echonest.remix.audio as audio

usage = """
Usage: 
    python sarabande.py <input_filename> <output_filename>

Example:
    python sarabande.py EverythingIsOnTheOne.mp3 EverythingIsReallyOnTheOne.mp3
"""

def main(input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    bars = audiofile.analysis.bars
    collect = audio.AudioQuantumList()
    for bar in bars:
	try:
            collect.append(bar.children()[1])
	except IndexError:
	    pass
    out = audio.getpieces(audiofile, collect)
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
