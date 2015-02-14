"""
part2b.py
Fixes a weird aspect of Musescore-generated MIDI files where a note_off event and a note_on event supposed to happen concurrently are one MIDI clock apart instead of zero.

Jesse David Sykes, 14 February 2015
"""

import sys

usage = """
Usage: 
    python part2b.py <input_txt>

Example:
    python part2b.py BWV552_p2.txt
"""

def main(input_filename):
	with open(input_filename,'r') as input:
		line = input.readline()
		output = open(line.split('\n')[0]+'_p2b.txt','w')
		output.write(line)
		events = []
		line = input.readline()
		while line != "End of file\n":
			sections = line.split(' ')
			if sections[0] == "Start":
				output.write('\n' + line)
			elif sections[0] == "note_on" or sections[0] == "note_off":
				events.append(line.split(' '))
			elif sections[0] == "End":
				# loop through events, changing times as necessary, then write them to file
				i = 0
				while i < (len(events) - 1):
					if int(events[i+1][2]) - int(events[i][2]) == 1:
						events[i][2] = events[i+1][2]
						i = i - 1
					else:
						i = i + 1
				for event in events:
					output.write(' '.join(event))
				output.write(line)
				events = []
			line = input.readline()
		output.write(line)
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