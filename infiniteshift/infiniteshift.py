"""
infiniteshift.py
Plays sections of three user-defined songs for a user-defined amount of time, pitch and tempo shifting as necessary.

Jesse David Sykes, 23 April 2015

This module uses a modified version of aqplayer by Luke Stack, adding a function to both tempo and pitch shift before playing.
"""

import echonest.remix.audio as audio
from aqplayer import Player
import random
import sys
import fractions

usage = """
Usage: 
    python infiniteshift.py <input_mp3_1> <input_mp3_2> <input_mp3_3> <time_in_minutes>

Example:
    python infiniteshift.py BWV552.mp3 BWV522.mp3 BWV525.mp3 5
"""

def main(input1, input2, input3, time):
	threshold = 250
	track1 = audio.LocalAudioFile(input1)
	track2 = audio.LocalAudioFile(input2)
	track3 = audio.LocalAudioFile(input3)
	fsegs = [[],[],[]]
	segments = [track1.analysis.segments,track2.analysis.segments,track3.analysis.segments]
	sections = [track1.analysis.sections,track2.analysis.sections,track3.analysis.sections]
	for i in range(len(sections)):
		j = 0
		for section in sections[i]:
			while segments[i][j].start + segments[i][j].duration < section.start:
				j += 1
			fsegs[i].append(segments[i][j])
	adjlists = [[],[],[]]
	for i in range(len(sections)):
		for section in sections[i]:
			adjlists[i].append([])
	for i in range(len(sections)):
		for j in range(len(sections[i])):
			adjlists[i][j].append([i, j, 1.0, 0])
			p1, t1, lb1, lm1, d1 = fsegs[i][j].pitches, fsegs[i][j].timbre, fsegs[i][j].loudness_begin, fsegs[i][j].loudness_max, fsegs[i][j].duration
			tp1, k1, m1, ts1, ln1 = sections[i][j].tempo, sections[i][j].key, sections[i][j].mode, sections[i][j].time_signature, sections[i][j].loudness
			compoundUp1 = len(sections[i][j].children()[0].children()) % 3 == 0
			compoundDown1 = len(sections[i][j].children()[0].children()[0].children()) % 3 == 0
			while tp1 >= 120:
				tp1 = tp1 / (3 if compoundUp1 else 2)
			while tp1 < 40:
				tp1 = tp1 * (3 if compoundDown1 else 2)
			if tp1 < 60:
				tp1 = tp1 * 2
			for k in range(j + 1, len(sections[i])):
				p2, t2, lb2, lm2, d2 = fsegs[i][k].pitches, fsegs[i][k].timbre, fsegs[i][k].loudness_begin, fsegs[i][k].loudness_max, fsegs[i][k].duration
				tp2, k2, m2, ts2, ln2 = sections[i][k].tempo, sections[i][k].key, sections[i][k].mode, sections[i][k].time_signature, sections[i][k].loudness
				compoundUp2 = len(sections[i][k].children()[0].children()) % 3 == 0
				compoundDown2 = len(sections[i][k].children()[0].children()[0].children()) % 3 == 0
				while tp2 >= 120:
					tp2 = tp2 / (3 if compoundUp2 else 2)
				while tp2 < 40:
					tp2 = tp2 * (3 if compoundDown2 else 2)
				if tp2 < 60:
					tp2 = tp2 * 2
				dp, dt, db, dm, dd = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1), abs(d2 - d1)
				dtp, dk, dm, dts, dln = abs(tp2 - tp1), k2 - k1, abs(m2 - m1), 1/fractions.gcd(ts2, ts1), abs(ln2 - ln1)
				if dk < 6:
					dk += 12
				if dk > 6:
					dk -= 12
				for l in range(12):
					dp = dp + (p2[l] - p1[l])**2
					dt = dt + (t2[l] - t1[l])**2
				dp = dp**0.5
				pshift = False
				if dk != 0:
					dps = 0
					for l in range(12):
						dps = dps + (p2[(i-dk)%12] - p1[i])**2
					dps = dps**0.5
					if dps < dp:
						dp = dps
						pshift = True
				dist = dp*10 + (dt**0.5) + db + dm + dd*100 + dtp*10 + abs(dk)*10 + dm + dts + dln
				if dist < threshold:
					adjlists[i][j].append([i, k, tp2/tp1*1.0, (dk if pshift else 0)])
					adjlists[i][k].append([i, j, tp1/tp2*1.0, (-dk if pshift else 0)])
	for i1 in range(len(sections)):
		for i2 in range(i1+1, len(sections)):
			for j in range(len(sections[i1])):
				p1, t1, lb1, lm1, d1 = fsegs[i1][j].pitches, fsegs[i1][j].timbre, fsegs[i1][j].loudness_begin, fsegs[i1][j].loudness_max, fsegs[i1][j].duration
				tp1, k1, m1, ts1, ln1 = sections[i1][j].tempo, sections[i1][j].key, sections[i1][j].mode, sections[i1][j].time_signature, sections[i1][j].loudness
				compoundUp1 = len(sections[i][j].children()[0].children()) % 3 == 0
				compoundDown1 = len(sections[i][j].children()[0].children()[0].children()) % 3 == 0
				while tp1 >= 120:
					tp1 = tp1 / (3 if compoundUp1 else 2)
				while tp1 < 40:
					tp1 = tp1 * (3 if compoundDown1 else 2)
				if tp1 < 60:
					tp1 = tp1 * 2
				for k in range(len(sections[i2])):
					p2, t2, lb2, lm2, d2 = fsegs[i2][k].pitches, fsegs[i2][k].timbre, fsegs[i2][k].loudness_begin, fsegs[i2][k].loudness_max, fsegs[i2][k].duration
					tp2, k2, m2, ts2, ln2 = sections[i2][k].tempo, sections[i2][k].key, sections[i2][k].mode, sections[i2][k].time_signature, sections[i2][k].loudness
					compoundUp2 = len(sections[i][k].children()[0].children()) % 3 == 0
					compoundDown2 = len(sections[i][k].children()[0].children()[0].children()) % 3 == 0
					while tp2 >= 120:
						tp2 = tp2 / (3 if compoundUp2 else 2)
					while tp2 < 40:
						tp2 = tp2 * (3 if compoundDown2 else 2)
					if tp2 < 60:
						tp2 = tp2 * 2
					dp, dt, db, dm, dd = 0, 0, abs(lb2 - lb1), abs(lm2 - lm1), abs(d2 - d1)
					dtp, dk, dm, dts, dln = abs(tp2 - tp1), k2 - k1, abs(m2 - m1), 1/fractions.gcd(ts2, ts1), abs(ln2 - ln1)
					if dk < 6:
						dk += 12
					if dk > 6:
						dk -= 12
					for l in range(12):
						dp = dp + (p2[l] - p1[l])**2
						dt = dt + (t2[l] - t1[l])**2
					dp = dp**0.5
					pshift = False
					if dk != 0:
						dps = 0
						for l in range(12):
							dps = dps + (p2[(i-dk)%12] - p1[i])**2
						dps = dps**0.5
						if dps < dp:
							dp = dps
							pshift = True
					dist = dp*10 + (dt**0.5) + db + dm + dd*100 + dtp*10 + abs(dk)*10 + dm + dts + dln
					if dist < threshold:
						adjlists[i1][j].append([i2, k, tp2/tp1*1.0, (dk if pshift else 0)])
						adjlists[i2][k].append([i1, j, tp1/tp2*1.0, (-dk if pshift else 0)])
	collect = []
	duration = 0
	i = [random.choice([0,1,2]),0,1.0,0]
	secdur = sections[i[0]][i[1]].duration
	newi = i
	curr_pshift = 0
	while duration + secdur < time:
		if i[1] + 1 == len(sections[i[0]]):
			newi = [random.choice([0,1,2]), 0, 1, 0]
			pshift = 0
		else:
			newi = random.choice(adjlists[i[0]][i[1]+1])
			pshift = newi[3] - curr_pshift
		tshift = newi[2]
		if pshift > 6:
			pshift -=  12
		if pshift < -6:
			pshift += 12
		for bar in sections[i[0]][i[1]].children():
			if bar == sections[i[0]][i[1]].children()[-1]:
				numbeats = len(bar.children())
				stepratio = tshift ** (1.0 / numbeats)
				for i, beat in enumerate(bar.children()):
					collect.append([beat, stepratio ** i, curr_pshift])
			else:
				for beat in bar.children():
					collect.append([beat, 1.0, curr_pshift])
		duration = duration + secdur
		i = newi
		secdur = sections[i[0]][i[1]].duration
		curr_pshift = pshift
	aqp = Player()
	for beat in collect:
		aqp.shift_and_play(beat[0], beat[1], beat[2])
	aqp.close_stream()

if __name__ == '__main__':
	try:
		input_one = sys.argv[1]
		input_two = sys.argv[2]
		input_three = sys.argv[3]
		length = float(sys.argv[4])
	except:
		print usage
		sys.exit(-1)
	main(input_one, input_two, input_three, length*60.0)