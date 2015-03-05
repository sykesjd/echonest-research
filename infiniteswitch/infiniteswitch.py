"""
infiniteswitch.py
Plays sections of two user-provided songs for a user defined amount of time.

Jesse David Sykes, 5 March 2015

This code uses aqplayer.py by Luke Stack, 17 February 2015
"""

import echonest.remix.audio as audio
from aqplayer import Player
import random
import sys
import fractions

usage = """
Usage: 
    python infiniteswitch.py <input_mp3_1> <input_mp3_2> <time_in_minutes>

Example:
    python infiniteswitch.py UnderPressure.mp3 IceIceBaby.mp3 5
"""

def main(input_one, input_two, length):
	threshold = 290
	track_one = audio.LocalAudioFile(input_one)
	track_two = audio.LocalAudioFile(input_two)
	fsegs = [[],[]]
	segments = [track_one.analysis.segments,track_two.analysis.segments]
	sections = [track_one.analysis.sections,track_two.analysis.sections]
	for i in range(len(sections)):
		j = 0
		for section in sections[i]:
			while segments[i][j].start + segments[i][j].duration < section.start:
				j = j + 1
			fsegs[i].append(segments[i][j])
	adjlists = [[],[]]
	for i in range(len(sections)):
		for j in range(len(sections[i])):
			adjlists[i].append([])
			p1, t1, lb1, lm1, d1 = fsegs[i][j].pitches, fsegs[i][j].timbre, fsegs[i][j].loudness_begin, fsegs[i][j].loudness_max, fsegs[i][j].duration
			tp1, k1, m1, ts1, ln1 = sections[i][j].tempo, sections[i][j].key, sections[i][j].mode, sections[i][j].time_signature, sections[i][j].loudness
			for k in range(len(sections[i])):
				if j == 1 and k == 1: # workaround for a weird bug
					adjlists[i][j].append([i,k])
				elif j == k and k != len(sections) - 1:
					adjlists[i][j].append([i,k])
				elif k != len(sections) - 1:
					p2, t2, lb2, lm2, d2 = fsegs[i][k].pitches, fsegs[i][k].timbre, fsegs[i][k].loudness_begin, fsegs[i][k].loudness_max, fsegs[i][k].duration
					tp2, k2, m2, ts2, ln2 = sections[i][k].tempo, sections[i][k].key, sections[i][k].mode, sections[i][k].time_signature, sections[i][k].loudness
					dp, dt, db, dm, dd = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1), abs(d2 - d1)
					dtp, dk, dm, dts, dln = abs(tp2 - tp1), min(abs(k2 - k1), 12 - abs(k2 - k1)), abs(m2 - m1), 1/fractions.gcd(ts2, ts1), abs(ln2 - ln1)
					for l in range(12):
						dp = dp + (p2[l] - p1[l])**2
						dt = dt + (t2[l] - t1[l])**2
					dist = (dp**0.5)*10 + (dt**0.5) + db + dm + dd*100 + dtp*10 + dk*100 + dm + dts + dln
					if dist < threshold:
						adjlists[i][j].append([i,k])
	for i in range(len(sections[0])):
		p1, t1, lb1, lm1, d1 = fsegs[0][i].pitches, fsegs[0][i].timbre, fsegs[0][i].loudness_begin, fsegs[0][i].loudness_max, fsegs[0][i].duration
		tp1, k1, m1, ts1, ln1 = sections[0][i].tempo, sections[0][i].key, sections[0][i].mode, sections[0][i].time_signature, sections[0][i].loudness
		for j in range(len(sections[1])):
			p2, t2, lb2, lm2, d2 = fsegs[1][j].pitches, fsegs[1][j].timbre, fsegs[1][j].loudness_begin, fsegs[1][j].loudness_max, fsegs[1][j].duration
			tp2, k2, m2, ts2, ln2 = sections[1][j].tempo, sections[1][j].key, sections[1][j].mode, sections[1][j].time_signature, sections[1][j].loudness
			dp, dt, db, dm, dd = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1), abs(d2 - d1)
			dtp, dk, dm, dts, dln = abs(tp2 - tp1), min(abs(k2 - k1), 12 - abs(k2 - k1)), abs(m2 - m1), 1/fractions.gcd(ts2, ts1), abs(ln2 - ln1)
			for k in range(12):
				dp = dp + (p2[k] - p1[k])**2
				dt = dt + (t2[k] - t1[k])**2
			dist = (dp**0.5)*10 + (dt**0.5) + db + dm + dd*100 + dtp*10 + dk*100 + dm + dts + dln
			if dist < threshold:
				if j != len(sections[1]) - 1:
					adjlists[0][i].append([1,j])
				if i != len(sections[0]) - 1:
					adjlists[1][j].append([0,i])
	collect = []
	duration = 0
	i = [0,0]
	secdur = sections[i[0]][i[1]].duration
	while duration + secdur < length:
		collect.append([i[0],sections[i[0]][i[1]]])
		duration = duration + secdur
		newi = random.choice(adjlists[i[0]][i[1]+1])
		while newi[1] == len(sections[newi[0]]) - 1 or len(adjlists[newi[0]][newi[1]+1]) == 0:
			newi = random.choice(adjlists[i[0]][i[1]+1])
		i = newi
		secdur = sections[i[0]][i[1]].duration
	aqp = [Player(track_one),Player(track_two)]
	for section in collect:
		aqp[section[0]].play(section[1])
	aqp[0].closeStream()
	aqp[1].closeStream()

if __name__ == '__main__':
	try:
		input_one = sys.argv[1]
		input_two = sys.argv[2]
		length = float(sys.argv[3])
	except:
		print usage
		sys.exit(-1)
	main(input_one, input_two, length*60.0)