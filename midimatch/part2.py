"""
part2.py
Converts the time values in the p1 file from relative values to absolute values for the p2 file.

Jesse David Sykes, 13 February 2015
"""

import sys

usage = """
Usage: 
    python part2.py <input_txt>

Example:
    python part2.py BWV552_p1.txt
"""

def main(input_filename):
	output = open(input_filename.split('_')[0]+'_p2.txt','w')
	output.write(input_filename.split('_')[0]+'\n')
	with open(input_filename,'r') as input:
		timesum = 0
		for line in input:
			eventtype = line.split(' ')[0]
			if eventtype == "Start":
				output.write('\n'+line)
			elif eventtype == "End":
				timesum = 0
				output.write(line)
			elif eventtype == "note_on" or eventtype == "note_off":
				# add time to timesum, write line to output replacing time with timesum
				sections = line.split(":")
				timesum = timesum + int(sections[4].split('\n')[0])
				# writes 'note_on ' or 'note_off '
				output.write(sections[0].split(' ')[0]+" ")
				# writes note number
				output.write(sections[2].split(',')[0]+" ")
				# writes timestamp then newline
				output.write(str(timesum)+"\n")
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