# echonest-research

This repository contains research modules testing the capabilities of the Echonest and Echonest Remix APIs in Python Anaconda. The modules currently contained are:

* sarabande - a trial module set up when this repository was created; takes an mp3 file and outputs a 'sarabande' mp3 file
* infinitestop - matches similar sections of "For What It's Worth" and plays section by section like Infinite Jukebox plays beat by beat, except for a predetermined amount of time
* infiniteswitch - matches similar sections between two songs and plays section by section for a predetermined amount of time
* gradualswitch - transitions between two sections of different tempi by gradually changing the tempo throughout the last bar of the first section toward the tempo of the second section; also pitch shifts second section to match key of first

The repository also contains inquiry reports pertaining to research performed for the class corresponding to this repository. The inquiries currently contained are:

* 17 February 2015 - a look into how Infinite Jukebox compares beats and how to extend the algorithm to the section level
* 03 March 2015 - a look into how to expand beyond Infinite Jukebox's comparison method for comparing sections using section-level data
* 24 March 2015 - a look into how Remix shifts pitch and tempo for audio quanta