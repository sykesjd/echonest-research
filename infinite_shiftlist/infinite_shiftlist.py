__author__ = 'parryrm, ed. sykesjd'

import os
import bisect
from scipy.sparse import dok_matrix, find
import hashlib
import pickle
import sys
import threading
from aqplayer import Player
import urllib2
from spotipy import Spotify
import echonest.remix.audio as audio
import shutil
import re
from numpy import hstack, array, diag, ones, minimum, isnan, copy, where, vstack, all, repeat, roll
from scipy.spatial.distance import pdist, cdist, squareform, euclidean, cityblock
from time import sleep
from pyechonest.util import EchoNestAPIError
from operator import itemgetter
from random import random, choice
from matplotlib.pyplot import figure, plot, show
import getopt

AUDIO_EXTENSIONS = {'mp3', 'm4a', 'wav', 'ogg', 'au', 'mp4'}
PLAYLIST_DIR = 'playlist'
THRESHOLD = 150
SPOT_DIR = 'spotify'
SPOT_PLAY = PLAYLIST_DIR + os.sep + 'spotify.play.pkl'

def _is_audio(f_):
    _, ext = os.path.splitext(f_)
    ext = ext[1:]
    return ext in AUDIO_EXTENSIONS

def _is_playlist(f_):
    return re.search(r".*\.play\.pkl", f_) is not None

def _is_md5(x_):
    return re.match('[a-z0-9]{32}', x_) is not None

def get_md5(song_file_):
    return hashlib.md5(file(song_file_, 'rb').read()).hexdigest()

def get_all_songs(directory_):
    all_songs_ = []
    for f_ in os.listdir(directory_):
        path_ = os.path.join(directory_, f_)
        if os.path.isdir(path_):
            all_songs_.extend(get_all_songs(path_))
        elif _is_audio(path_):
            all_songs_.append(path_)
    return all_songs_

def get_sections(audio_file_):
    aq_secs_ = audio_file_.analysis.sections
    aq_segs_ = audio_file_.analysis.segments
    # find the first segment for each section
    fsegs_ = []
    j = 0
    for sec in aq_secs_:
        while aq_segs_[j].start + aq_segs_[j].duration < sec.start:
            j += 1
        fsegs_.append(aq_segs_[j])
    # collect all info from sections and first segments
    nseg_ = len(fsegs_)
    nsec_ = len(aq_secs_)
    pitches_ = array([seg_.pitches for seg_ in aq_segs_ if seg_ in fsegs_])
    timbre_ = array([seg_.timbre for seg_ in aq_segs_ if seg_ in fsegs_])
    duration_ = array([seg_.duration for seg_ in aq_segs_ if seg_ in fsegs_]).reshape((nseg_, 1))
    loudness_max_ = array([seg_.loudness_max for seg_ in aq_segs_ if seg_ in fsegs_]).reshape((nseg_, 1))
    loudness_start_ = array([seg_.loudness_begin for seg_ in aq_segs_ if seg_ in fsegs_]).reshape((nseg_, 1))
    tempo_ = array([sec_.tempo for sec_ in aq_secs_]).reshape((nsec_, 1))
    key_ = array([sec_.key for sec_ in aq_secs_]).reshape((nsec_, 1))
    mode_ = array([sec_.mode for sec_ in aq_secs_]).reshape((nsec_, 1))
    timesig_ = array([sec_.time_signature for sec_ in aq_secs_]).reshape((nsec_, 1))
    secloud_ = array([sec_.loudness for sec_ in aq_secs_]).reshape((nsec_, 1))
    # return an ndarray with info for all sections
    return hstack((10 * pitches_, timbre_, 100 * duration_, loudness_max_, loudness_start_, tempo_, 10 * key_, mode_, timesig_, secloud_))

def sec_distances(u_, v_=None):
    if v_ is None:
        # comparing song with itself
        return sec_distances(u_, u_)
    else:
        # comparing two songs
        d_ = float('NaN') * ones((len(u_), len(v_), 3))
        for i, seci in enumerate(u_):
            for j, secj in enumerate(v_):
                # find tempo and pitch shifting values
                tshift = float(secj[27]) / float(seci[27])
                pshift = (secj[28] - seci[28]) / 10
                # finding pitch distance must account for possible difference in key
                pitchdist = euclidean(seci[0:12], secj[0:12])
                ps = False 
                if pshift != 0:
                    dps = euclidean(seci[0:12], roll(secj[0:12], pshift))
                    if dps < pshift:
                        pitchdist = dps
                        ps = True
                # find timbre distance, etc.
                timbredist = euclidean(seci[12:24], secj[12:24])
                restdist = cityblock(seci[24:31], secj[24:31])
                # distance reported with tempo and pitch shifting values
                d_[i][j] = [(pitchdist+timbredist+restdist), tshift, pshift if ps else 0]
        return d_

def get_sec_distances(audio_i_, audio_j_):
    sections_i = get_sections(audio_i_)
    sections_j = get_sections(audio_j_)
    section_dist_ = sec_distances(sections_i, sections_j)
    return section_dist_

def robust_local_audio_file(audio_file_):
    try:
        laf_ = audio.LocalAudioFile(audio_file_)
        return laf_
    except EchoNestAPIError:
        print "Failed to retrieve analysis... wait to try again"
        sleep(10)
        return robust_local_audio_file(audio_file_)

def get_local_audio(all_songs_):
    local_audio_ = {}
    for i_ in range(len(all_songs_)):
        print 'get song', (i_ + 1), '/', len(all_songs_)
        extension = os.path.splitext(all_songs_[i_])[1]
        track_md5_ = get_md5(all_songs_[i_])
        mp3_file = PLAYLIST_DIR + "/" + track_md5_ + extension
        if not os.path.isfile(mp3_file):
            print "copying original audio to", mp3_file
            if not os.path.exists(PLAYLIST_DIR):
                os.makedirs(PLAYLIST_DIR)
            shutil.copyfile(all_songs_[i_], mp3_file)
        print "loading local audio from", mp3_file
        laf_ = robust_local_audio_file(mp3_file)
        local_audio_[track_md5_] = laf_
    return local_audio_

def get_start_secs(local_audio_):
    start_ = 0
    start_secs_ = {}
    for md5_ in sorted(local_audio_.keys()):
        laf_ = local_audio_[md5_]
        start_secs_[md5_] = start_
        start_ += len(laf_.analysis.sections)
    start_secs_['total'] = start_
    return start_secs_

def update_edges(e_, m1_, i1_, m2_, i2_, d_):
    a = e_[m1_].get(i1_, [])
    # edge reported with distance value, md5, section number, tempo shifting value, and pitch shifting value
    bisect.insort(a, (d_[0], m2_, i2_, d_[1], d_[2]))
    e_[m1_][i1_] = a

def get_edges(laf_i_, laf_j_):
    md5_i_ = laf_i_.analysis.pyechonest_track.md5
    md5_j_ = laf_j_.analysis.pyechonest_track.md5
    track_md5 = [md5_i_, md5_j_]
    track_md5.sort()
    edges_file_ = PLAYLIST_DIR + os.sep + track_md5[0] + "_" + track_md5[1] + ".edges.pkl"
    if os.path.isfile(edges_file_):
        print "loading", edges_file_
        with open(edges_file_, 'rb') as in_file_:
            edges_ = pickle.load(in_file_)
    else:
        num_edges = 0
        edges_ = {md5_i_: {}, md5_j_: {}}
        sec_distances = get_sec_distances(laf_i_, laf_j_)
        sec_distances[isnan(sec_distances)] = float('Inf')
        (ii, jj) = where(sec_distances[:,:,0] < THRESHOLD)
        for (i1, j1) in vstack((ii, jj)).T:
            d1 = sec_distances[i1, j1]
            update_edges(edges_, md5_i_, i1, md5_j_, j1, d1)
            if md5_i_ != md5_j_:
                update_edges(edges_, md5_j_, j1, md5_i_, i1, d1)
            num_edges += 1
        edges_['num_edges'] = num_edges
        print num_edges, "edges found"
        with open(edges_file_, 'wb') as output_:
            pickle.dump(edges_, output_)
    return edges_

def check_edges_ij(edges_ij_, md5_, max_key_):
    if md5_ in edges_ij_.keys():
        keys_ = array(edges_ij_[md5_].keys())
        okay_ = keys_ < max_key_
        if not all(okay_):
            print md5_, 'not okay.'
            print keys_[not okay_]
            raise

def update_all_edges(edges_, edges_ij_):
    for md5_ in edges_ij_.keys():
        if not _is_md5(md5_):
            continue
        a = edges_.get(md5_, {})
        for md5_sec_ in edges_ij_[md5_].keys():
            edge_list_ = edges_ij_[md5_][md5_sec_]
            b = a.get(md5_sec_, [])
            for edge in edge_list_:
                bisect.insort(b, edge)
            a[md5_sec_] = b
        edges_[md5_] = a

def get_all_edges(local_audio_):
    edges_ = {}
    for md5_i_ in local_audio_.keys():
        for md5_j_ in local_audio_.keys():
            print md5_i_, ",", md5_j_
            edges_ij_ = get_edges(local_audio_[md5_i_], local_audio_[md5_j_])
            check_edges_ij(edges_ij_, u'3da35fa9caab917eaf70f10d1b35753c', 821)
            check_edges_ij(edges_ij_, u'aa84896e81aa15ca98ff631ffc643532', 693)
            update_all_edges(edges_, edges_ij_)
    return edges_

class EdgesThread(threading.Thread):
    def __init__(self, all_songs):
        threading.Thread.__init__(self)
        self.all_songs = all_songs
        self.edges = {}

    def run(self):
        for song_i_ in self.all_songs:
            laf_i_ = audio.LocalAudioFile(song_i_)
            for song_j_ in self.all_songs:
                laf_j_ = audio.LocalAudioFile(song_j_)
                edges_ij_ = get_edges(laf_i_, laf_j_)
                update_all_edges(self.edges, edges_ij_)

def get_all_edges_background(all_songs_):
        thread_ = EdgesThread(all_songs_)
        thread_.start()

def get_adjacency_matrix(all_edges_, start_secs_, threshold_):
    s_ = dok_matrix((start_secs_['total'], start_secs_['total']))
    md5_sorted_by_start = [x[0] for x in sorted(start_secs_.items(), key=itemgetter(1))]
    del md5_sorted_by_start[-1]
    for i_ in md5_sorted_by_start:
        edges = all_edges_[i_]
        for i1, sorted_list in edges.iteritems():
            for (d1, j, j1, t1, p1) in sorted_list:
                if d1 < threshold_:
                    s_[start_secs_[i_] + i1, start_secs_[j] + j1] = d1
    return s_

class Playback(object):
    threshold = THRESHOLD
    min_branch_probability = 0.18
    max_branch_probability = 0.50
    step_branch_probability = 0.09
    curr_branch_probability = min_branch_probability
    ghost = 1

    def __init__(self, all_edges_, local_audio_, aq_player_, start_secs_, thread=None, curr_md5=None, curr_sec=None):
        self.all_edges = all_edges_
        self.local_audio = local_audio_
        self.aq_player = aq_player_
        self.start_secs = start_secs_
        self.thread = thread
        self.curr_md5 = choice(self.all_edges.keys()) if curr_md5 is None else curr_md5
        self.curr_laf = self.local_audio[self.curr_md5]
        self.curr_sec = 0 if curr_sec is None else curr_sec
        self.last_branch = [self.curr_sec, self.curr_sec]
        self.tshift = 1.0
        self.curr_pshift = 0
        # variables necessary for determining tempo and pitch shifting values
        self.next_md5 = self.curr_md5
        self.next_sec = self.curr_sec
        self.next_lb = self.last_branch
        bars = self.curr_laf.analysis.sections[self.curr_sec].children()
        # last_bar holds the bar to be tempo shifted between sections
        self.last_bar = bars[-1]
        # sometimes a bar between sections is in neither section; must catch it
        next_lbar = self.curr_laf.analysis.bars[self.last_bar.absolute_context()[0]+1]
        if next_lbar != self.curr_laf.analysis.sections[self.curr_sec+1].children()[0]:
            self.last_bar = next_lbar
        # queue of beats to be played
        self.beat_queue = []
        for bar in bars:
            if bar != self.last_bar:
                # last bar omitted because we need to determine tempo shifting value first
                for beat in bar.children():
                    # for each beat, store md5, section number, the quantum, the tempo shifting value, the pitch shifting value, and the branch for the graph when playing
                    self.beat_queue.append([self.curr_md5, self.curr_sec, beat, 1.0, 0, self.last_branch])

    def update(self, *args):
        cursor_ = args[0]
        branch_cursor_ = args[1]
        last_branch_cursor_ = args[2]
        candidates = []
        branched = False
        if self.next_sec == self.curr_sec and self.next_md5 == self.curr_md5:
            # prnt_stmt will be printed at every section change
            prnt_stmt = "playing " + str(self.curr_md5) + " section " + str(self.curr_sec)
            # need to determine what the next section will be before adding last bar 
            self.next_sec = (self.curr_sec + 1) % len(self.curr_laf.analysis.sections)
            next_ps = 0 if self.next_sec == 0 else self.curr_pshift
            next_laf = self.local_audio[self.curr_md5]
            candidates = self.all_edges[self.curr_md5].get(self.next_sec, [])
            candidates = [candidates[i] for i in range(len(candidates)) if candidates[i][0] < self.threshold]
            if self.thread is not None:
                if self.thread.ejecting():
                    candidates = [candidates[i] for i in range(len(candidates)) if candidates[i][1] == self.curr_md5]
            changed_song = False
            if len(candidates) > 0:
                prnt_stmt = prnt_stmt + ", " + str(len(candidates)) + " branch candidates, prob = " + str(self.curr_branch_probability)
                if random() < self.curr_branch_probability:
                    prnt_stmt = prnt_stmt + ", branch incoming"
                    branch = choice(candidates)
                    changed_song = branch[1] != self.curr_md5
                    self.next_lb[0] = [self.curr_sec + self.start_secs[self.curr_md5]]
                    self.next_md5 = branch[1]
                    self.next_sec = branch[2]
                    self.tshift = branch[3]
                    next_ps = branch[4] - self.curr_pshift
                    next_laf = self.local_audio[self.next_md5]
                    self.curr_branch_probability = self.min_branch_probability
                    self.next_lb[1] = [self.next_sec + self.start_secs[self.next_md5]]
                    branched = True
                    if changed_song:
                        self.next_lb = [self.next_sec, self.next_sec]
                else:
                    self.curr_branch_probability = min(self.max_branch_probability, self.curr_branch_probability + self.step_branch_probability)
            # now we know tempo shifting value: add last_bar's beats
            last_beats = self.last_bar.children()
            stepratio = self.tshift ** (1.0 / len(last_beats))
            for j, beat in enumerate(last_beats):
                self.beat_queue.append([self.curr_md5, self.curr_sec, beat, stepratio ** j, self.curr_pshift, self.last_branch])
            # find next value for last_bar
            next_bars = next_laf.analysis.sections[self.next_sec].children()
            next_lbar = next_bars[-1]
            if next_laf.analysis.sections[self.next_sec] != next_laf.analysis.sections[-1]:
                pnlbar = next_laf.analysis.bars[next_lbar.absolute_context()[0]+1]
                if pnlbar != next_laf.analysis.sections[self.next_sec+1].children()[0]:
                    next_lbar = pnlbar
            # add beats for next section, with appropriate pitch shifting
            for bar in next_bars:
                if bar != next_lbar:
                    for beat in bar.children():
                        self.beat_queue.append([self.next_md5, self.next_sec, beat, 1.0, next_ps, self.next_lb])
            # update pitch shifting value and last_bar
            self.curr_pshit = next_ps
            self.last_bar = next_lbar
            print prnt_stmt
        # remove first beat in queue and play, updating necessary fields
        beat_to_play = self.beat_queue.pop(0)
        changed_song = self.curr_md5 != beat_to_play[0]
        self.curr_md5 = beat_to_play[0]
        self.curr_laf = self.local_audio[self.curr_md5]
        self.curr_sec = beat_to_play[1]
        self.last_branch = self.next_lb if branched else self.last_branch
        if changed_song:
            print "********** Changed song **********"
        self.aq_player.shift_and_play(beat_to_play[2], beat_to_play[3], beat_to_play[4])
        if changed_song and self.thread is not None:
            self.thread.eject(self.curr_md5)
        # update graph
        t0 = self.curr_sec + self.start_secs[self.curr_md5]
        cursor_.set_xdata(t0)
        cursor_.set_ydata(t0)
        if len(candidates) > 0:
            t0 = repeat(t0, len(candidates), 0)
            t1 = array([self.start_secs[c[1]] for c in candidates]) + array([c[2] for c in candidates])
            branch_x = vstack((t0, t0, t1, t1, t0)).T.reshape((-1, 1))
            branch_y = vstack((t0, t1, t1, t0, t0)).T.reshape((-1, 1))
            branch_cursor_.set_xdata(branch_x)
            branch_cursor_.set_ydata(branch_y)
            self.ghost = 1
        elif self.ghost >= 4:
            branch_cursor_.set_xdata([])
            branch_cursor_.set_ydata([])
        else:
            self.ghost += 1
        if branched:
            if self.last_branch[0] < self.last_branch[1]:
                last_branch_cursor_.set_color('green')
            else:
                last_branch_cursor_.set_color('red')
            last_branch_x = [self.last_branch[i] for i in [0, 1, 1]]
            last_branch_y = [self.last_branch[i] for i in [0, 0, 1]]
            last_branch_cursor_.set_xdata(last_branch_x)
            last_branch_cursor_.set_ydata(last_branch_y)
        args[0].figure.canvas.draw()

def infinite_playlist(playlist_name, playlist_directory=None):
    all_edges_file = PLAYLIST_DIR + "/" + playlist_name + ".play.pkl"
    all_edges = None
    if os.path.isfile(all_edges_file):
        print "loading playlist edges"
        with open(all_edges_file, 'rb') as input_:
            all_edges = pickle.load(input_)
        all_songs = [PLAYLIST_DIR + os.sep + md5 + '.mp3' for md5 in all_edges.keys()]
    else:
        all_songs = get_all_songs(playlist_directory)
    print len(all_songs), "songs"
    aq_player = Player()
    local_audio = {}
    try:
        local_audio = get_local_audio(all_songs)
        start_secs = get_start_secs(local_audio)
        print start_secs['total'], "total sections"
        if not os.path.isfile(all_edges_file):
            all_edges = get_all_edges(local_audio)
            with open(all_edges_file, 'wb') as output:
                pickle.dump(all_edges, output)
        total_edges = 0
        for song_i in all_edges.keys():
            song_i_edges = all_edges[song_i]
            for sec_i in song_i_edges.keys():
                song_i_sec_i_edges = song_i_edges[sec_i]
                for _, song_j, sec_j, ts_j, ps_j in song_i_sec_i_edges:
                    total_edges += 1
        print total_edges, "total edges"
        s = get_adjacency_matrix(all_edges, start_secs, THRESHOLD)
        fig = figure()
        ax = fig.add_subplot(111)
        ax.spy(s, markersize=1)
        x = sorted(start_secs.values() * 2)[1:]
        y = sorted(start_secs.values() * 2)[:-1]
        boundaries = [0, 0]
        boundaries[0], = plot(x, y, marker='None', linestyle='-', color='gray')
        boundaries[1], = plot(y, x, marker='None', linestyle='-', color='gray')
        branch_cursor, = plot([], [], color='cyan', marker='s', markersize=5, linestyle='-')
        last_branch_cursor, = plot([], [], color='green', marker='s', markersize=5)
        cursor, = plot([], [], color='magenta', marker='s', markersize=5, linestyle='None')
        dt = 0.001
        playback = Playback(all_edges, local_audio, aq_player, start_secs)
        timer = fig.canvas.new_timer(interval=dt*1000.0)
        timer.add_callback(playback.update, cursor, branch_cursor, last_branch_cursor)
        timer.start()
        show()
    finally:
        print "cleaning up"
        print "closing aq_player stream"
        aq_player.close_stream()
        for laf in local_audio.values():
            print "unloading local audio"
            laf.unload()

class DataLoadingThread(threading.Thread):
    def __init__(self, sim, boundaries, edges, local_audio, aq_player, start_secs, curr_md5):
        print "creating new thread"
        threading.Thread.__init__(self)
        self.sim = sim
        self.boundaries = boundaries
        self.edges = edges
        self.local_audio = local_audio
        self.aq_player = aq_player
        self.start_secs = start_secs
        self.curr_md5 = curr_md5
        self._ejecting = threading.Event()
        self._stopping = threading.Event()
    
    def update(self):
        for sec, edges in self.edges[self.curr_md5].items():
            self.edges[self.curr_md5][sec] = [edge for edge in edges if edge[1] == self.curr_md5]
        for md5 in self.edges.keys():
            if md5 != self.curr_md5:
                del self.edges[md5]
        for md5, laf in self.local_audio.items():
            if md5 != self.curr_md5:
                laf.unload()
                del self.local_audio[md5]
        for md5 in self.start_secs.keys():
            if md5 != self.curr_md5:
                del self.start_secs[md5]
        self.start_secs[self.curr_md5] = 0
        self.start_secs['total'] = len(self.local_audio[self.curr_md5].analysis.sections)
    
    def run(self):
        print "thread is running"
        while True:
            edge_files = [f for f in os.listdir(PLAYLIST_DIR)
                          if re.search(r"" + self.curr_md5 + ".*\.edges.pkl", f) is not None]
            edge_files = edge_files[:50]
            for edge_file in edge_files:
                print "load edge_file:", edge_file
                new_md5 = None
                m = re.match(r"" + self.curr_md5 + "_([a-z0-9]{32})", edge_file)
                if m is not None:
                    new_md5 = m.group(1)
                m = re.match(r"([a-z0-9]{32})_" + self.curr_md5, edge_file)
                if m is not None:
                    new_md5 = m.group(1)
                if new_md5 == self.curr_md5:
                    continue
                audio_file = PLAYLIST_DIR + os.sep + new_md5 + '.mp3'
                self.local_audio[new_md5] = audio.LocalAudioFile(audio_file)
                new_edges = get_edges(self.local_audio[self.curr_md5], self.local_audio[new_md5])
                update_all_edges(self.edges, new_edges)
                new_edges = get_edges(self.local_audio[new_md5], self.local_audio[new_md5])
                update_all_edges(self.edges, new_edges)
                new_edges = get_edges(self.local_audio[new_md5], self.local_audio[self.curr_md5])
                update_all_edges(self.edges, new_edges)
                self.start_secs[new_md5] = self.start_secs['total']
                self.start_secs['total'] += len(self.local_audio[new_md5].analysis.sections)
                s = get_adjacency_matrix(self.edges, self.start_secs, THRESHOLD)
                fs = find(s)
                self.sim.set_data(fs[0], fs[1])
                self.sim.figure.gca().set_xlim([0, self.start_secs['total']])
                self.sim.figure.gca().set_ylim([self.start_secs['total'], 0])
                x = sorted(self.start_secs.values() * 2)[1:]
                y = sorted(self.start_secs.values() * 2)[:-1]
                self.boundaries[0].set_xdata(x)
                self.boundaries[0].set_ydata(y)
                self.boundaries[1].set_xdata(y)
                self.boundaries[1].set_ydata(x)
                print "************** REDRAW SELF-SIMILARITY ********************"
                self.sim.figure.canvas.draw()
                if self.ejecting() or self.stopping():
                    break
            self._ejecting.wait()
            if self.stopping():
                break
            self.update()
            self._ejecting.clear()
    
    def eject(self, curr_md5):
        self.curr_md5 = curr_md5
        self._ejecting.set()

    def ejecting(self):
        return self._ejecting.isSet()

    def stop(self):
        self._stopping.set()
        self._ejecting.set()
        
    def stopping(self):
        return self._stopping.isSet()

def infinite_out_of_core(curr_md5):
    audio_file = PLAYLIST_DIR + os.sep + curr_md5 + '.mp3'
    curr_local_audio = {}
    curr_aq_player = Player()
    thread = None
    try:
        curr_local_audio = get_local_audio([audio_file])
        curr_edges = get_all_edges(curr_local_audio)
        curr_start_secs = {curr_md5: 0, 'total': len(curr_local_audio[curr_md5].analysis.sections)}
        s = get_adjacency_matrix(curr_edges, curr_start_secs, THRESHOLD)
        fig = figure()
        ax = fig.add_subplot(111)
        sim = ax.spy(s, markersize=1)
        x = sorted(curr_start_secs.values() * 2)[1:]
        y = sorted(curr_start_secs.values() * 2)[:-1]
        boundaries = [0, 0]
        boundaries[0], = plot(x, y, marker='None', linestyle='-', color='gray')
        boundaries[1], = plot(y, x, marker='None', linestyle='-', color='gray')
        branch_cursor, = plot([], [], color='cyan', marker='s', markersize=5, linestyle='-')
        last_branch_cursor, = plot([], [], color='green', marker='s', markersize=5)
        cursor, = plot([], [], color='magenta', marker='s', markersize=5, linestyle='None')
        thread = DataLoadingThread(sim, boundaries, curr_edges, curr_local_audio,
                                   curr_aq_player, curr_start_secs, curr_md5)
        dt = 0.001
        playback = Playback(curr_edges, curr_local_audio, curr_aq_player, curr_start_secs, thread=thread)
        timer = fig.canvas.new_timer(interval=dt*1000.0)
        timer.add_callback(playback.update, cursor, branch_cursor, last_branch_cursor)
        timer.start()
        thread.start()
        show()
    finally:
        print "cleaning up"
        if thread is not None:
            thread.stop()
            if thread.isAlive():
                thread.join()
        print "closing aq_player stream"
        aq_player.close_stream()
        for laf in curr_local_audio.values():
            print "unloading local audio"
            laf.unload()

def get_album(artist_uri, spot, playlist_dir):
    clear_spot_cache()
    results = spot.artist_albums(artist_uri)
    for i in range(len(results)):
        print i, results[u'items'][i][u'name']
    a_index = input('Enter album index: ')
    album = results[u'items'][a_index]
    tracks = spot.album_tracks(album[u'uri'])[u'items']
    get_spot_tracks(tracks)

def clear_spot_cache():
    if not os.path.exists(SPOT_DIR):
        os.makedirs(SPOT_DIR)
    else:
        shutil.rmtree(SPOT_DIR)
        os.makedirs(SPOT_DIR)
    if os.path.isfile(SPOT_PLAY):
        os.remove(SPOT_PLAY)

def get_spot_tracks(tracks):
    for t in tracks:
        try:
            url = t[u'preview_url']
            req2 = urllib2.Request(url)
            response = urllib2.urlopen(req2)
            data = response.read()
            mp3_file = SPOT_DIR + os.sep + t['name'] + '.mp3'
            with open(mp3_file, 'wb') as output_:
                output_.write(data)
            print 'track:' + t['name']
        except:
            pass

def get_top_ten(artist_uri, spot, playlist_dir):
    clear_spot_cache()
    results = spot.artist_top_tracks(artist_uri)
    tracks = results[u'tracks'][:10]
    get_spot_tracks(tracks)

def spot_search(output):
    artist = raw_input("Please enter artist: ")
    spot = Spotify()
    results = spot.search(q='artist:' + artist, type='artist')
    print "Found:", results[u'artists'][u'items'][0][u'name']
    artist_uri = results[u'artists'][u'items'][0][u'uri']
    choice = raw_input("Top 10 [T] or album [A]: ")
    if choice == 't' or choice == 'T':
        get_top_ten(artist_uri, spot, output)
    else:
        get_album(artist_uri, spot, output)
    print "Found:", results[u'artists'][u'items'][0][u'name']

def main():
    print sys.argv
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'o:', ["output="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    input_ = args[0]
    output = "playlist"
    for o, a in optlist:
        if o in ("-p", "--output"):
            output = a
        else:
            assert False, "unhandled option"
    if re.match('spotify', input_, re.IGNORECASE):
        output = SPOT_DIR
        spot_search(output)
        infinite_playlist(output, output)
    else:
        if os.path.isdir(input_):
            infinite_playlist(output, input_)
        elif os.path.isfile(input_):
            if _is_audio(input_):
                track_md5_ = get_md5(input_)
                infinite_out_of_core(track_md5_)
            else:
                infinite_playlist(input_)
        else:
            infinite_out_of_core(input_)

def usage():
    print 'usage: python infinite_playlist.py <input> [OPTION]'
    print
    print '<input>'
    print '\tThe input directory, playlist file, song file, md5, or \'spotify\''
    print
    print 'Options:'
    print '-o, --output='
    print '\tThe output playlist file name (default: "playlist")'

if __name__ == '__main__':
    sys.exit(main())