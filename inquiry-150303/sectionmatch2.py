"""
sectionmatch2.py

Finds the first segments of every section in two tracks then plots similarity matrices for within each song and between the songs.

Jesse David Sykes, 13 February 2015
"""

import echonest.remix.audio as audio
import matplotlib.pyplot as plt
from matplotlib import numpy
import fractions

usage = """
Usage: 
    python sectionmatch2.py <input_mp3_1> <input_mp3_2> <output_name>

Example:
    python sectionmatch2.py BWV552.mp3 BWV577.mp3 SSM552-577
"""

def main(input_one, input_two, output_name):
	trackone = audio.LocalAudioFile(input_one)
	tracktwo = audio.LocalAudioFile(input_two)
	sectionsone, segmentsone = trackone.analysis.sections, trackone.analysis.segments
	fsegsone, i = [], 0
	for section in sectionsone:
		while segmentsone[i].start + segmentsone[i].duration < section.start:
			i = i + 1
		fsegsone.append(segmentsone[i])
	sectionstwo, segmentstwo = tracktwo.analysis.sections, tracktwo.analysis.segments
	fsegstwo, i = [], 0
	for section in sectionstwo:
		while segmentstwo[i].start + segmentstwo[i].duration < section.start:
			i = i + 1
		fsegstwo.append(segmentstwo[i])
	ssmone, ssmtwo, ssmonetwo = [], [], []
	for i in range(len(sectionsone)):
		p1, t1, lb1, lm1, d1 = fsegsone[i].pitches, fsegsone[i].timbre, fsegsone[i].loudness_begin, fsegsone[i].loudness_max, fsegsone[i].duration
		tp1, k1, m1, ts1, ln1 = sectionsone[i].tempo, sectionsone[i].key, sectionsone[i].mode, sectionsone[i].time_signature, sectionsone[i].loudness
		for j in range(len(sectionsone)):
			p2, t2, lb2, lm2, d2 = fsegsone[j].pitches, fsegsone[j].timbre, fsegsone[j].loudness_begin, fsegsone[j].loudness_max, fsegsone[j].duration
			tp2, k2, m2, ts2, ln2 = sectionsone[j].tempo, sectionsone[j].key, sectionsone[j].mode, sectionsone[j].time_signature, sectionsone[j].loudness
			dp, dt, db, dm, dd = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1), abs(d2 - d1)
			dtp, dk, dm, dts, dln = abs(tp2 - tp1), min(abs(k2 - k1), 12 - abs(k2 - k1)), abs(m2 - m1), 1/fractions.gcd(ts2, ts1), abs(ln2 - ln1)
			for k in range(12):
				dp = dp + (p2[k] - p1[k])**2
				dt = dt + (t2[k] - t1[k])**2
			dist = (dp**0.5)*10 + (dt**0.5) + db + dm + dd*100 + dtp*10 + dk*100 + dm + dts + dln
			ssmone.append(dist)
	for i in range(len(sectionstwo)):
		p1, t1, lb1, lm1, d1 = fsegstwo[i].pitches, fsegstwo[i].timbre, fsegstwo[i].loudness_begin, fsegstwo[i].loudness_max, fsegstwo[i].duration
		tp1, k1, m1, ts1, ln1 = sectionstwo[i].tempo, sectionstwo[i].key, sectionstwo[i].mode, sectionstwo[i].time_signature, sectionstwo[i].loudness
		for j in range(len(sectionstwo)):
			p2, t2, lb2, lm2, d2 = fsegstwo[j].pitches, fsegstwo[j].timbre, fsegstwo[j].loudness_begin, fsegstwo[j].loudness_max, fsegstwo[j].duration
			tp2, k2, m2, ts2, ln2 = sectionstwo[j].tempo, sectionstwo[j].key, sectionstwo[j].mode, sectionstwo[j].time_signature, sectionstwo[j].loudness
			dp, dt, db, dm, dd = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1), abs(d2 - d1)
			dtp, dk, dm, dts, dln = abs(tp2 - tp1), min(abs(k2 - k1), 12 - abs(k2 - k1)), abs(m2 - m1), 1/fractions.gcd(ts2, ts1), abs(ln2 - ln1)
			for k in range(12):
				dp = dp + (p2[k] - p1[k])**2
				dt = dt + (t2[k] - t1[k])**2
			dist = (dp**0.5)*10 + (dt**0.5) + db + dm + dd*100 + dtp*10 + dk*100 + dm + dts + dln
			ssmtwo.append(dist)
	for i in range(len(sectionsone)):
		p1, t1, lb1, lm1, d1 = fsegsone[i].pitches, fsegsone[i].timbre, fsegsone[i].loudness_begin, fsegsone[i].loudness_max, fsegsone[i].duration
		tp1, k1, m1, ts1, ln1 = sectionsone[i].tempo, sectionsone[i].key, sectionsone[i].mode, sectionsone[i].time_signature, sectionsone[i].loudness
		for j in range(len(sectionstwo)):
			p2, t2, lb2, lm2, d2 = fsegstwo[j].pitches, fsegstwo[j].timbre, fsegstwo[j].loudness_begin, fsegstwo[j].loudness_max, fsegstwo[j].duration
			tp2, k2, m2, ts2, ln2 = sectionstwo[j].tempo, sectionstwo[j].key, sectionstwo[j].mode, sectionstwo[j].time_signature, sectionstwo[j].loudness
			dp, dt, db, dm, dd = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1), abs(d2 - d1)
			dtp, dk, dm, dts, dln = abs(tp2 - tp1), min(abs(k2 - k1), 12 - abs(k2 - k1)), abs(m2 - m1), 1/fractions.gcd(ts2, ts1), abs(ln2 - ln1)
			for k in range(12):
				dp = dp + (p2[k] - p1[k])**2
				dt = dt + (t2[k] - t1[k])**2
			dist = (dp**0.5)*10 + (dt**0.5) + db + dm + dd*100 + dtp*10 + dk*100 + dm + dts + dln
			ssmonetwo.append(dist)
	ssmone = numpy.array(ssmone).reshape(len(fsegsone), len(fsegsone))
	ssmtwo = numpy.array(ssmtwo).reshape(len(fsegstwo), len(fsegstwo))
	ssmonetwo = numpy.array(ssmonetwo).reshape(len(fsegsone), len(fsegstwo))
	plt.imshow(ssmone, 'gray')
	plt.title('Section Distance Within ' + input_one)
	plt.colorbar()
	plt.savefig(output_name+'_one')
	plt.show()
	plt.imshow(ssmtwo, 'gray')
	plt.title('Section Distance Within ' + input_two)
	plt.colorbar()
	plt.savefig(output_name+'_two')
	plt.show()
	plt.imshow(ssmonetwo, 'gray')
	plt.title('Section Distance Between ' + input_one + ' and ' + input_two)
	plt.colorbar()
	plt.savefig(output_name+'_onetwo')
	plt.show()

if __name__ == '__main__':
    import sys
    try:
        input_one = sys.argv[1]
        input_two = sys.argv[2]
        output_name = sys.argv[3]
    except:
        print usage
        sys.exit(-1)
    main(input_one, input_two, output_name)