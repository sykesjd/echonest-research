# midimatch
This module stores the work for an ongoing experiment that will theoretically culminate in being able to produce a piano roll animation for a piece of classical music given a MIDI representation and an MP3 recording of a performance. The multi-step process should go something like this:

1. Converting a MIDI file to a text file: This step is performed with the use of the Echonest Remix MIDI package. The resulting text file will for every track list every note_on and note_off event on its own line, with the time of each event stored as the delta-time relative to the last event.

2. Converting the relative times to 'absolute' times: This file processing procedure will change the labelled times from delta-times to absolute times along the duration of the MIDI file.

3. Converting multi-track format to single-track format: This operation will essentially sort all the events in order of absolute time.

4. Gathering segment data from MP3: Alongside step 3, this action will grab the Echonest analysis of the MP3 file and extract the segment data.

5. Matching the events to the segments: Here is the step that is not yet entirely clear. Theoretically, the start of each segment should correspond to a note_on or note_off event in the MIDI file, but that is not an absolute certainty. If it is the case, then this step will produce a file similar to the file produced in 3, except instead of the time being in MIDI-clocks, the time will be in either milliseconds or microseconds (haven't decided yet).

6. Converting single-track back into multi-track: This procedure will involve matching events in the file obtained from step 5 to events in the file produced in step 2 to split the data back into multi-track format, which will allow for a multi-color animation denoting different tracks in the final product.

7. Converting track data into a 'notes object': This operation will take the multi-track data and produce a JSON object that will store all the notes for every track in a format that will be easily readable for the final product. Perhaps there will be a gcd operation performed on the length values, but that concept is still under construction.

8. Creating piano roll from notes object (the final product): This action will be performed in JavaScript onto an HTML canvas for a web-viewable creation. The script will place a rectangle on the screen for every note from the note_on point to the note_off point as stored in the JSON object.

Any input is greatly appreciated.