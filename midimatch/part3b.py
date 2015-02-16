"""
part3b.py
Fixes a weird aspect of Musescore-generated MIDI files where a note_off event and a note_on event supposed to happen concurrently are one MIDI clock apart instead of zero.

Jesse David Sykes, 14 February 2015
"""

import sys

usage = """
Usage: 
    python part3b.py <input_txt>

Example:
    python part3b.py BWV552_p3.txt
"""

def main(input_filename):
	with open(input_filename,'r') as input:
		line = input.readline()
		output = open(line.split('\n')[0]+'_p3b.txt','w')
		output.write(line + '\n')
		events = []
		for line in input:
			parts = line.split(' ')
			if parts[0] == 'note_on' or parts[0] == 'note_off':
				events.append(parts)
		i = 0
		while i < (len(events) - 1):
			if int(events[i+1][2]) - int(events[i][2]) == 1:
				events[i][2] = events[i+1][2]
				i = i - 1
			else:
				i = i + 1
		for event in events:
			output.write(' '.join(event))
		output.close()

if __name__ == '__main__':
    try:
        input_filename = sys.argv[1]
        if input_filename.split('.')[1] != 'txt':
        	print "Not a text file"
        	sys.exit(-1)
    except:
        print usage
        sys.exit(-1)
    main(input_filename)