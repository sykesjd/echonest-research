# Problem
We want to be able to determine the similarity of different sections the same way Infinite Jukebox compares beats.

# Question
1. How does Infinite Jukebox compare beats?
2. Can the same method be applied to compare sections?

# Resources
1. [Infinite Jukebox Inline JS]
2. [AudioQuantum in Echonest Remix API]
3. [JRemixer Used by Infinite Jukebox]

### 1. Mini-abstract and relevance of [Infinite Jukebox Inline JS]
Examining the inline Javascript on the Infinite Jukebox page, we can see that IJ is comparing the pitches, timbre, and loudness of the first segments of each beat. However, the code does not make clear how those first segments are determined, so question 1 is only partially answered.

### 2. Mini-abstract and relevance of [AudioQuantum in Echonest Remix API]
A look at the Echonest Remix API for the AudioQuantum class reveals the following about its `children()` method:
> Returns an AudioQuantumList of the AudioQuanta that it contains, one step down the hierarchy. A `beat` returns `tatum`s, a `bar` returns `beat`s, and a `section` returns `bar`s.

This information reveals that segments are not actually placed within the hierarchy structure of quantum types, so finding the first segment of a beat is not as easy as chaining calls to `children()`.

### 3. Mini-abstract and relevance of [JRemixer Used by Infinite Jukebox]
Revisiting the Infinite Jukebox, we find an external Javascript file that does the work of finding the first segment of a beat. The code is included below:
```javascript
var last = 0;
var quanta = track.analysis[quanta_name];
var segs = track.analysis.segments;
for (var i = 0; i < quanta.length; i++) {
	var q = quanta[i]
	q.overlappingSegments = [];

	for (var j = last; j < segs.length; j++) {
		var qseg = segs[j];
		// seg starts before quantum so no
		if ((qseg.start + qseg.duration) < q.start) {
			continue;
		}
		// seg starts after quantum so no
		if (qseg.start > (q.start + q.duration)) {
			break;
		}
		last = j;
		q.overlappingSegments.push(qseg);
	}
}
```
For each beat, this unintuitively written block of code goes through the segments and stops at the last segment that starts before or on the beat, then pushes that segment to the first segments list. This Javascript answers question 1, and I wrote a python script that does the same thing at the section level to show that the answer to question 2 is yes. The inner `for` loop in the JS is refactored into a more intuitive `while` loop in the python.

[Infinite Jukebox Inline JS]: http://labs.echonest.com/Uploader/index.html
[AudioQuantum in Echonest Remix API]: http://echonest.github.io/remix/apidocs/echonest.remix.audio.AudioQuantum-class.html
[JRemixer Used by Infinite Jukebox]: http://static.echonest.com.s3.amazonaws.com/js/jremix.js?v5