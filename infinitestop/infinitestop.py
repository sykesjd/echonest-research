"""
infinitestop.py
Plays sections of Buffalo Springfield's "For What It's Worth" for a user-defined amount of time.

By Jesse David Sykes, 19 February 2015

This code uses aqplayer.py by Luke Stack, 17 February 2015
"""

import echonest.remix.audio as audio
from aqplayer import Player
import random
import sys

usage = """
Usage: 
    python infinitestop.py <time_in_minutes>

Example:
    python infinitestop.py 5
"""

def main(fwiw, length, aqp):
	fsegs = []
	i = 0
	segments = fwiw.analysis.segments
	sections = fwiw.analysis.sections
	for section in sections:
		while segments[i].start + segments[i].duration < section.start:
			i = i + 1
		fsegs.append(segments[i])
	adjlists = []
	j = 0
	for s1 in fsegs:
		adjlists.append([])
		p1, t1, lb1, lm1 = s1.pitches, s1.timbre, s1.loudness_begin, s1.loudness_max
		k = 0
		for s2 in fsegs:
			if j != k and k < len(sections) - 1:
				p2, t2, lb2, lm2 = s2.pitches, s2.timbre, s2.loudness_begin, s2.loudness_max
				dp, dt, db, dm = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1)
				for i in range(12):
					dp = dp + (p2[i] - p1[i])**2
					dt = dt + (t2[i] - t1[i])**2
				dist = (dp**0.5) + (dt**0.5) + db + dm
				if dist < 120:
					adjlists[j].append(k)
			elif j < len(sections) - 1:
				adjlists[j].append(k)
			k = k + 1
		j = j + 1
	collect = []
	collect.append(sections[0])
	duration = sections[0].duration
	i = 1
	secdur = sections[i].duration
	while duration + secdur < length:
		collect.append(sections[i])
		duration = duration + secdur
		try:
			i = random.choice(adjlists[i+1])
		except:
			main(fwiw, length, aqp)
			aqp.closeStream()
			sys.exit(0)
		secdur = sections[i].duration
	collect.append(sections[2].children()[-1].children()[-1].children()[-1])
	collect.append(sections[3].children()[0].children()[0].children()[0])
	for section in collect:
		aqp.play(section)

if __name__ == '__main__':
	try:
		length = float(sys.argv[1])
	except:
		print usage
		sys.exit(-1)
	fwiw = audio.LocalAudioFile('FWIW.mp3')
	aqp = Player(fwiw)
	main(fwiw, length*60.0, aqp)
	aqp.closeStream()