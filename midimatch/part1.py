"""
part1.py
Reads in MIDI file and output a text file.

Jesse David Sykes, 13 February 2015
"""

import sys
import echonest.remix.support.midi.MidiInFile as MidiInFile
import echonest.remix.support.midi.MidiToText as MidiToText

usage = """
Usage: 
    python part1.py <input_mid>

Example:
    python part1.py BWV552.midi
"""

"""
Tee: provides a means of piping standard output into a text file.

Usage:
	f = open('file','w')
	original = sys.stdout
	sys.stdout = Tee(sys.stdout, f)
	print "appears in file"
	sys.stdout = original
	print "doesn't appear in file"
	f.close()

Courtesy of Thrustmaster on StackOverflow, 4 Jul 2012
"""
class Tee(object):
	def __init__(self, *files):
		self.files = files
	def write(self, obj):
		for f in self.files:
			f.write(obj)

def main(input_filename):
	midiIn = MidiInFile.MidiInFile(MidiToText.MidiToText(), input_filename)
	f = open(input_filename.split('.')[0]+'_p1.txt','w')
	original = sys.stdout
	sys.stdout = Tee(sys.stdout, f)
	midiIn.read()
	sys.stdout = original
	f.close()

if __name__ == '__main__':
    try:
        input_filename = sys.argv[1]
        if input_filename.split('.')[1] != 'mid':
        	print "Not a standard MIDI file"
        	sys.exit(-1)
    except:
        print usage
        sys.exit(-1)
    main(input_filename)