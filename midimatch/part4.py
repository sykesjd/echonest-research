"""
part4.py
Saves MP3 segment start times to a text file.

Jesse David Sykes, 14 February 2015
"""

import sys
import echonest.remix.audio as audio

usage = """
Usage: 
    python part4.py <input_mp3>

Example:
    python part4.py BWV552.mp3
"""

def main(input_filename):
	with open(input_filename.split('.')[0]+'_p4.txt','w') as output:
		output.write(input_filename.split('.')[0]+'\n\n')
		track = audio.LocalAudioFile(input_filename)
		for segment in track.analysis.segments:
			output.write(str(segment.start)+'\n')

if __name__ == '__main__':
    try:
        input_filename = sys.argv[1]
        if input_filename.split('.')[1] != 'mp3':
        	print "Not an MP3 file"
        	sys.exit(-1)
    except:
        print usage
        sys.exit(-1)
    main(input_filename)