"""
testpypitch.py
A test module for pypitch.

Jesse David Sykes, 10 April 2015
"""

import os
import sys
from echonest.remix import audio
from pypitch import PyPitch

usage = """
Usage: 
    python testpypitch.py <input_mp3> <no_of_semitones>

Example:
    python testpypitch.py BWV552.mp3 -2
"""

def main(input, semitones):
	track = audio.LocalAudioFile(input)
	collect = []
	for section in track.analysis.sections:
		section_data = section.render().data
		new_data = PyPitch.shiftPitchSemiTones(section_data, semitones)
		ts = audio.AudioData(ndarray = new_data, shape = new_data.shape, sampleRate = track.sampleRate, numChannels = new_data.shape[1])
		collect.append(ts)
	out = audio.assemble(collect, numChannels = 2)
	out.encode(input.split('.')[0] + '_' + ('d' if semitones < 0 else 'u') + str(abs(semitones)) + '.mp3')

if __name__ == '__main__':
	try:
		input = sys.argv[1]
		semitones = int(sys.argv[2])
	except:
		print usage
		sys.exit(-1)
	main(input, semitones)