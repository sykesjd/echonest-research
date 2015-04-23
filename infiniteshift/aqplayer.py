__author__ = 'lukestack, ed. jessedavidsykes'
import sys
import pyaudio
import numpy as np
import dirac
from pypitch import PyPitch

class Player:
	def __init__(self):
		if sys.platform == 'linux2':
			import ossaudiodev
			self.stream = ossaudiodev.open('w')
			self.stream.setparameters(ossaudiodev.AFMT_S16_LE, 2, 44100)
		else:
			self.p = pyaudio.PyAudio()
			self.stream = self.p.open(format=self.p.get_format_from_width(2), channels=2, rate=44100, output=True)

	def shift_tempo_and_play(self, audio_quantum, ratio):
		ad = audio_quantum.render()
		scaled_beat = dirac.timeScale(ad.data, ratio)
		self.stream.write(scaled_beat.astype(np.int16).tostring())

	def shift_semitones_and_play(self, audio_quantum, semitones):
		ad = audio_quantum.render()
		new_data = PyPitch.shiftPitchSemiTones(ad.data, semitones)
		self.stream.write(new_data.astype(np.int16).tostring())

	def shift_octaves_and_play(self, audio_quantum, octaves):
		ad = audio_quantum.render()
		new_data = PyPitch.shiftPitchOctaves(ad.data, octaves)
		self.stream.write(new_data.astype(np.int16).tostring())

	def shift_and_play(self, audio_quantum, ratio, semitones):
		ad = audio_quantum.render()
		new_data = PyPitch.shiftPitchSemiTones(dirac.timeScale(ad.data, ratio), semitones)
		self.stream.write(new_data.astype(np.int16).tostring())
	
	def play(self, audio_quantum):
		ad = audio_quantum.render()
		self.stream.write(ad.data.tostring())

	def close_stream(self):
		self.stream.close()
		if self.p is not None:
			self.p.terminate()