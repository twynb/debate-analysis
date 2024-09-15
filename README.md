# Presidential Debate Analysis

This is a short analysis of a transcript of the presidential debate between Kamala Harris and Donald Trump on September 10, 2024.

The analysis includes, for both candidates and both moderators:

- The total number of words said
- The 20 most used words, excluding some uninteresting words
- The 20 most used words, excluding some uninteresting words and pronouns
  - Note that singular first-person pronouns are already part of the "uninteresting words"
- The [Flesch Reading Ease](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests) score
- The [Flesch-Kincaid grade level](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests) score

Additionally, the 20 words with the biggest difference between how often Trump said them versus how often Harris did, and vice versa, are computed.

Please do me a favor and, if you have the time and motivation, apply this analysis to other presidential debates.
Note that you will need to tweak the parsing code a bit, depending on your transcript's format.

## LICENSE

The [analysis script](./debate_anlyz.py) is licensed under the BSD 3-Clause license, see [LICENSE](./LICENSE).

The CMU Dictionary used for the syllable calculation for the Flesch-Kincaid readability tests is also licensed under the BSD 3-Clause license, see [LICENSE_CMUDICT](./LICENSE_CMUDICT).

The original debate transcript belongs to [abc11.com](https://abc11.com/read-harris-trump-presidential-debate-transcript/15289001/).
