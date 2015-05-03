"""
pypitch.py
Provides a means of shifting the pitch of given audio.

Jesse David Sykes, 10 April 2015
"""

import dirac
import numpy

class PyPitch(object):
	@staticmethod
	def shiftPitchSemiTones(audio_data, semitones):
		while semitones > 6:
			semitones = semitones - 12
		while semitones < -6:
			semitones = 12 + semitones
		if semitones == 0:
			return audio_data
		factor = 2.0 ** (semitones / 12.0)
		stretched_data = dirac.timeScale(audio_data, factor)
		index = numpy.floor(numpy.arange(0, stretched_data.shape[0], factor)).astype('int32')
		new_data = stretched_data[index]
		return new_data
	
	@staticmethod
	def shiftPitchOctaves(audio_data, octaves):
		if octaves == 0:
			return audio_data
		factor = 2.0 ** octaves
		stretched_data = dirac.timeScale(audio_data, factor)
		index = numpy.floor(numpy.arange(0, stretched_data.shape[0], factor)).astype('int32')
		new_data = stretched_data[index]
		return new_data

