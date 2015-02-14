"""
part3.py
Takes multitrack text file and merges tracks to produce a single-track text file.

Jesse David Sykes, 14 February 2015
"""

import sys

usage = """
Usage: 
    python part3.py <input_txt>

Example:
    python part3.py BWV552_p2b.txt
"""

def main(input_filename):
	with open(input_filename,'r') as input:
		line = input.readline()
		output = open(line.split('\n')[0]+'_p3.txt','w')
		output.write(line+'\n')
		tracks = []
		i = -1
		line = input.readline()
		while line != "End of file\n":
			sections = line.split(' ')
			if sections[0] == "Start":
				i = i + 1
				tracks.append([])
			elif sections[0] == "note_on" or sections[0] == "note_off":
				tracks[i].append(sections)
			line = input.readline()
		notes = tracks[0]
		tracks.pop(0)
		while len(tracks) > 0:
			notes = merge(notes, tracks[0])
			tracks.pop(0)
		for note in notes:
			output.write(' '.join(note))
		output.close()

def merge(a1, a2):
	a3 = []
	i1 = 0
	i2 = 0
	while i1 < len(a1) and i2 < len(a2):
		if int(a2[i2][2]) < int(a1[i1][2]):
			a3.append(a2[i2])
			i2 = i2 + 1
		else:
			a3.append(a1[i1])
			i1 = i1 + 1
	while i1 < len(a1):
		a3.append(a1[i1])
		i1 = i1 + 1
	while i2 < len(a2):
		a3.append(a2[i2])
		i2 = i2 + 1
	return a3

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