# Problem
Now that it is possible to pitch shift our songs, we need to modify the section distance calculation to account for possible shifts.

# Questions
1. How are pitch and key accounted for already?
2. What needs to change to account for pitch shifting?

# Resources

1. [Infinite Switch Module]

#### Mini-abstract and relevance of [Infinite Switch Module]

In a previous research module, I used the most recent version of the section distance calculation, with the exception of the reduction of the weight on the tempo difference to account for tempo shifting. The following is a paraphrase of what the file does with segment pitch and section key:

```python
p1, p2 = seg1.pitches, seg2.pitches
k1, k2 = sec1.key, sec2.key
dp = 0
for i in range(12):
	dp = dp + (p2[i] - p1[i])^2
dp = dp ** 0.5
dk = min(abs(k2-k1), 12-abs(k2-k1))

dpWeight = 10
dkWeight = 100
```

### Discussion

With the capabilities of pypitch now available, the calculations above need to be edited. For starters, the absolute value operations on `dk` should be removed so that we can determine shift direction, only taking the absolute value when adding `dk` to the total distance. We can simplify like so:

```python
dk = k2-k1
if dk < -6:
	dk = dk + 12
if dk > 6:
	dk = dk - 12
```

The calculation for pitch distance should also be modified to account for key shift. However, a key shift may not be necessary even if the keys are different: the pitch vectors may be closer to each other pre-shift. To account for this, we will need a boolean flag, like so:

```python
pshift = False
dp = 0
for i in range(12):
	dp = dp + (p2[i] - p1[i])^2
dp = dp ** 0.5
if dk != 0:
	dps = 0
	for i in range(12):
		dps = dps + (p2[(i-dk)%12] - p1[i])^2
	dps == dps ** 0.5
	if dps < dp:
		dp = dps
		pshift = True
```

Additionally, the weight on the difference in keys should be lowered from 100 to 10 to indicate that key shifting is possible, but not exactly preferable.

After this, when reporting edges, in addition to reporting the to and from sections, we need to report by how much to shift the pitch. The difference is illustrated below:

```python
# i is index of song1, j is index of song2, k is the index of sec1, l is the index of sec2
# old way
adjlists[i][k].append([j,l])
adjlists[j][l].append([i,k])
# new way
adjlists[i][k].append([j,l,(dk if pshift else 0)])
adjlists[j][l].append([i,k,(-dk if pshift else 0)])
```

In the final player application, `dk` will be used to determine whether and by how much to shift the pitch of a section to play. Also in the player, a running variable - call it `cdk` - will keep track of how much the pitch has been shifted for the currently playing section, which will ensure the next section will be shifted by the correct amount.

[Infinite Switch Module]: https://github.com/sykesjd/echonest-research/blob/master/infiniteswitch/infiniteswitch.py