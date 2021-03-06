"""
gradualswitch.py
Plays first section of one song and the last section of another song,
	altering the tempo of the last few beats of the first section to
	create a gradual change between tempi; second section is key shifted
	to match key of first section.

Jesse David Sykes, 26 March 2015
"""

import os
import sys
import dirac
from echonest.remix import audio
from aqplayer import Player

usage = """
Usage: 
    python gradualswitch.py <input_mp3_1> <input_mp3_2>

Example:
    python gradualswitch.py BWV552.mp3 BWV522.mp3
"""

def main(input_one, input_two):
	track_one = audio.LocalAudioFile(input_one)
	track_two = audio.LocalAudioFile(input_two)
	section_one = track_one.analysis.sections[0]
	section_two = track_two.analysis.sections[-1]
	tempo_one = section_one.tempo
	tempo_two = section_two.tempo
	tempo_diff = tempo_two - tempo_one
	bars_one = section_one.children()
	collect = []
	for bar in bars_one:
		if bar == bars_one[-1]:
			numbeats = len(bar.children())
			step = tempo_diff/numbeats
			for i, beat in enumerate(bar.children()):
				beat_audio = beat.render()
				ratio = (tempo_one + step*(i+1))/(tempo_one + step*i)
				scaled_beat = dirac.timeScale(beat_audio.data, ratio)
				new_beat = audio.AudioData(ndarray=scaled_beat, shape=scaled_beat.shape, sampleRate=track_one.sampleRate, numChannels=scaled_beat.shape[1])
				collect.append(new_beat)
			break
		for beat in bar.children():
			collect.append(beat.render())
	out_data_one = audio.assemble(collect, numChannels=2)
	out_name_one = input_one.split('.')[0]+'-stretch.mp3'
	out_data_one.encode(out_name_one)
	play_one = audio.LocalAudioFile(out_name_one)
	aqp_one = Player(play_one)
	aqp_two = Player(track_two)
	beats_one = play_one.analysis.beats
	for beat in beats_one:
		aqp_one.play(beat)
	aqp_one.closeStream()
	aqp_two.play(section_two)
	aqp_two.closeStream()

if __name__ == '__main__':
	try:
		input_one = sys.argv[1]
		input_two = sys.argv[2]
	except:
		print usage
		sys.exit(-1)
	main(input_one, input_two)