"""
sectionmatch.py

Finds the first segments of every section in a track then plots two SSM matrices for pitch and timbre by section.

Jesse David Sykes, 13 February 2015
"""

import echonest.remix.audio as audio
import matplotlib.pyplot as plt
from matplotlib import numpy

usage = """
Usage: 
    python sectionmatch.py <input_mp3> <output_name>

Example:
    python sectionmatch.py BWV552.mp3 SSM552
"""

def main(input_filename, output_filename):
	track = audio.LocalAudioFile(input_filename)
	sections, segments = track.analysis.sections, track.analysis.segments
	fsegs, i = [], 0
	for section in sections:
		while segments[i].start <= section.start:
			i = i + 1
		fsegs.append(segments[i-1])
	ssmp, ssmt, p1, p2, t1, t2 = [], [], [], [], [], []
	for s1 in fsegs:
		p1, t1 = s1.pitches, s1.timbre
		for s2 in fsegs:
			p2, t2 = s2.pitches, s2.timbre
			distp, distt = 0, 0
			for j in range(len(p1)):
				distp = distp + (p2[j] - p1[j])**2
			for k in range(len(t1)):
				distt = distt + (t2[k] - t1[k])**2
			ssmp.append(distp**0.5)
			ssmt.append(distt**0.5)
	ssmp = numpy.array(ssmp).reshape(len(fsegs), len(fsegs))
	ssmt = numpy.array(ssmt).reshape(len(fsegs), len(fsegs))
	plt.imshow(ssmp, 'gray')
	plt.title('Section SSM (Pitches)')
	plt.colorbar()
	plt.savefig(output_filename+'_pitch')
	plt.show()
	plt.imshow(ssmt, 'gray')
	plt.title('Section SSM (Timbre)')
	plt.colorbar()
	plt.savefig(output_filename+'_timbre')
	plt.show()

if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)