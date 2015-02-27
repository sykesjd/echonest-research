# Problem
We want to expand on the current method of comparing sections to fit the requirements of comparing sections of multiple songs.

# Questions
1. What is already provided in a song's analysis at the level of a section's first segment?
2. What is additionally provided in a song's analysis at the section level?
3. How do we use what is additionally provided to say if two sections are similar?

# Resources

1. [Infinite Jukebox Inline JS]
2. [EchoNest Analyzer Documentation]

### 1. Mini-abstract and relevance of [Infinite Jukebox Inline JS]
We already know what is provided at the segment level from analyzing Infinite Jukebox's Javascript code in the last inquiry report. The relevant code is below:
```javascript
var timbreWeight = 1, pitchWeight = 10, 
    loudStartWeight = 1, loudMaxWeight = 1, 
    durationWeight = 100, confidenceWeight = 1;

function get_seg_distances(seg1, seg2) {
    var timbre = seg_distance(seg1, seg2, 'timbre', true);
    var pitch = seg_distance(seg1, seg2, 'pitches');
    var sloudStart = Math.abs(seg1.loudness_start - seg2.loudness_start);
    var sloudMax = Math.abs(seg1.loudness_max - seg2.loudness_max);
    var duration = Math.abs(seg1.duration - seg2.duration);
    var confidence = Math.abs(seg1.confidence - seg2.confidence);
    var distance = timbre * timbreWeight + pitch * pitchWeight + 
        sloudStart * loudStartWeight + sloudMax * loudMaxWeight + 
        duration * durationWeight + confidence * confidenceWeight;
    return distance;
}
```
Infinite Jukebox computes the distance between two segments by computing the Euclidean distances between their pitch vectors and their timbre vectors, computing the absolute differences between their loudnesses, durations, and confidences, then adds all those distances with certain weights. We saw with InfiniteStop that this method can be applied at the section level as well by analyzing the first segment of each section. This answers question 1.

### 2. Mini-abstract and relevance of [EchoNest Analyzer Documentation]
The documentation to EchoNest's Analyzer API says the following about sections:
> Sections are defined by large variations in rhythm or timbre, e.g. chorus, verse, bridge, guitar solo, etc. Each section contains its own descriptions of tempo, key, mode, time_signature, and loudness.

From this we can answer question 2: provided by the analysis at the section level is tempo, key, mode, time signature, and loudness. How important are each of these characteristics in determining the similarity of two sections?
* Tempo: relatively important. If the two sections are of wildly different tempi, chances are the transition from one section's predecessor to the other section would be rather jarring. I would assign the weight of 10, in Infinite Jukebox terms. Introducing the ability to change the tempo of a section with Remix would change how we treat tempo, but for now we can say the difference in tempi multiplied by 10 can be added to the distance between sections.
* Key: very important. Expecting to go into one key and suddenly ending up in another would make for a discordant transition indeed. I would assign a weight of 100, in Infinite Jukebox terms. Introducing the ability to change the key of a section with Remix would change how we treat key, but for now we can say the difference in keys multiplied by 100 can be added to the distance between sections.
* Mode: relatively unimportant. Expecting C major and getting C minor, for example, is a common occurence in Western music, so it would not necessarily make a bad transition. I would assign a weight of 1, in Infinite Jukebox terms.
* Time Signature: relatively unimportant. Changes in time signature are also a staple in Western music, so a transition between time signatures would not necessarily be bad. I would assign a weight of 1, in Infinite Jukebox terms.
* Loudness: Infinite Jukebox already has a weight of 1 on each of the segment-level loudness attributes, so it would be safe to have the same weight at the section level.

Included with this report is a python script that takes two songs and outputs three images: two plots of distances between sections within each song and one plot of distances between sections between the two songs.

[Infinite Jukebox Inline JS]: http://labs.echonest.com/Uploader/index.html
[EchoNest Analyzer Documentation]: http://developer.echonest.com/docs/v4/_static/AnalyzeDocumentation.pdf