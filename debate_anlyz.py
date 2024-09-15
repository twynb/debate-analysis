import re

REGEX_WORDS = re.compile(r"[^a-zA-Z0-9_']+")
SPEAKER_KEY_TRUMP = "FORMER PRESIDENT DONALD TRUMP"
SPEAKER_KEY_HARRIS = "VICE PRESIDENT KAMALA HARRIS"


def parse_file_to_speakers(file: str):
    """
    Parse all speakers from the given file.
    This will also cleanup some inconsistent naming from the ABC11 debate transcript.
    You will need to change or remove that part of the code when running the analysis on another transcript.
    """
    lines = {}
    with open(file, "r", encoding="utf-8") as input:
        for line in input.readlines():
            if line.startswith("#") or line == "":
                continue
            split = line.split(":", maxsplit=1)
            if len(split) != 2:
                continue
            if split[0] not in lines:
                lines[split[0]] = split[1]
            else:
                lines[split[0]] += " " + split[1]
    # cleanup inconsistent names for the same people
    lines[SPEAKER_KEY_HARRIS] += " " + lines.pop("VICE PRESIDENT HARRIS", "")
    lines["LINSEY DAVIS"] += " " + lines.pop("LINDSEY DAVIS", "")
    lines[SPEAKER_KEY_TRUMP] += " " + lines.pop("PRESIDENT TRUMP", "")
    return lines


SYLLABLES = {}


def init_cmu_dict():
    """
    Load the CMU dictionary and count the syllables for each word, to use in the analysis later.
    """
    with open("cmudict-0.7b", "r", encoding="cp1252") as cmudict:
        for line in cmudict.read().splitlines():
            split = re.split(r"\s+", line, maxsplit=1)
            if len(split) != 2:
                continue
            num_syllables = len(
                [
                    phoneme
                    for phoneme in re.split(r"\s+", split[1])
                    if phoneme != "" and phoneme[-1].isdigit()
                ]
            )
            SYLLABLES[split[0]] = num_syllables


def count_syllables(word: str):
    """
    Count the syllables in a word.
    If possible, use the count from the CMU dictionary.
    If not, lazily count the number of vowel groups.
    """
    if word.upper() in SYLLABLES:
        return SYLLABLES[word.upper()]
    # lazy approximation: just count the number of vowel groups
    # this would lead to errors for words like "date", but most words should be covered by the CMU dict anyway.
    return len(re.findall(r"[aeiou]+", word))


def flesch_params(input: str):
    """
    Gather the necessary parameters (sentence, word and syllable count) for the Flesch-Kincaid readability tests.
    """
    num_sentences = len(re.split(r"[\.?:!]+", input))
    words = [word for word in REGEX_WORDS.split(input) if word != ""]
    num_words = len(words)
    num_syllables = sum([count_syllables(word) for word in words])
    return (float(num_sentences), float(num_words), float(num_syllables))


def flesch_reading_ease(input: str):
    """
    Calculate the Flesch reading ease score for the given input.
    """
    (num_sentences, num_words, num_syllables) = flesch_params(input)
    return (
        206.835
        - 1.015 * (num_words / num_sentences)
        - 84.6 * (num_syllables / num_words)
    )


def flesch_kincaid_grade_level(input: str):
    """
    Calculate the Flesch-Kincaid grade level for the given input.
    """
    (num_sentences, num_words, num_syllables) = flesch_params(input)
    return (
        0.39 * (float(num_words) / float(num_sentences))
        + 11.8 * (float(num_syllables) / float(num_words))
        - 15.59
    )


BORING_WORDS = [
    "SO",
    "I",
    "I'M",
    "IS",
    "AND",
    "NOT",
    "THE",
    "YOU",
    "TOO",
    "THIS",
    "A",
    "TO",
    "WAS",
    "THAT",
    "IT",
    "HAVE",
    "ME",
    "WITH",
    "FOR",
    "OF",
    "BUT",
    "S",
    "MY",
    "JUST",
    "DO",
    "IN",
    "ON",
    "LL",
    "AS",
    "ARE",
    "T",
    "RE",
    "AT",
    "THEN",
    "BE",
    "BY",
    "WOULD",
    "HAD",
    "HAS",
    "AN",
]

PRONOUNS = [
    "YOU",
    "YOUR",
    "YOURS",
    "HE",
    "HIM",
    "HIS",
    "SHE",
    "HER",
    "HERS",
    "IT",
    "ITS",
    "IT'S",
    "WE",
    "OUR",
    "OURS",
    "THEY",
    "THEM",
    "THEIRS",
    "THAT'S",
]


def get_words_with_count(
    input: str,
    exclude_boring: bool = False,
    exclude_pronouns: bool = False,
    as_sorted: bool = True,
):
    """
    Get all words in the input, in upper case.
    By default, return them as a list of (str, int) tuples with the word and its count,
    sorted by the count in descending order.
    If `as_sorted` is set to false, return a dict mapping the words to their count.
    """
    split = REGEX_WORDS.split(input.upper())
    words = {}
    for word in split:
        if exclude_boring and word in BORING_WORDS:
            continue
        elif exclude_pronouns and word in PRONOUNS:
            continue
        elif word in words:
            words[word] = words[word] + 1
        else:
            words[word] = 1
    if as_sorted:
        return sorted(words.items(), key=lambda x: x[1], reverse=True)
    return words


def get_most_used_words(input: str, exclude_pronouns: bool = False):
    """
    Get the 20 most used words as a list or (str, int) tuples with the word and its count,
    excluding words in `BORING_WORDS`, from the input.
    If `exclude_pronouns` is True, also exclude the words in `PRONOUNS`.
    """
    words = get_words_with_count(
        input, exclude_boring=True, exclude_pronouns=exclude_pronouns
    )
    return words[0:20]


def get_total_word_count(input: str):
    """
    Get the total number of words in the input.
    """
    return len(REGEX_WORDS.split(input))

def get_total_syllable_count(input: str):
    """
    Get the total number of syllables in the input.
    """
    words = REGEX_WORDS.split(input)
    return sum([count_syllables(word) for word in words])


def get_words_with_deltas(input_a: str, input_b: str):
    """
    Get the 20 words with the biggest difference between how often they occur in `input_a`
    as opposed to `input_b`.
    """
    words_a = get_words_with_count(input_a)
    words_b = get_words_with_count(input_b, as_sorted=False)

    deltas = [
        [word[0], word[1] - (words_b[word[0]] if word[0] in words_b else 0)]
        for word in words_a
    ]
    deltas = sorted(deltas, key=lambda x: x[1], reverse=True)
    return deltas[0:20]


init_cmu_dict()

speakers = parse_file_to_speakers("debate_transcript.txt")

for speaker in speakers:
    print("===================================================================")
    print("Speaker: " + speaker)
    print("Number of words said: " + str(get_total_word_count(speakers[speaker])))
    print("Number of syllables said: " + str(get_total_syllable_count(speakers[speaker])))
    most_used_words = get_most_used_words(speakers[speaker])
    print(
        "Most used words: "
        + ", ".join(
            [word[0] + "(" + str(word[1]) + " times)" for word in most_used_words]
        )
    )
    most_used_non_pronouns = get_most_used_words(
        speakers[speaker], exclude_pronouns=True
    )
    print(
        "Most used non-pronoun words: "
        + ", ".join(
            [
                word[0] + "(" + str(word[1]) + " times)"
                for word in most_used_non_pronouns
            ]
        )
    )
    print("Flesch Reading Ease: " + str(flesch_reading_ease(speakers[speaker])))
    print(
        "Flesch-Kincaid Grade Level: "
        + str(flesch_kincaid_grade_level(speakers[speaker]))
    )

# everything from here on out will need to be changed for a different transcript!
print("===================================================================")
biggest_delta_harris_trump = get_words_with_deltas(
    speakers[SPEAKER_KEY_HARRIS], speakers[SPEAKER_KEY_TRUMP]
)
print(
    "Words Harris said more often than Trump: "
    + ", ".join(
        [
            word[0] + "(" + str(word[1]) + " times more)"
            for word in biggest_delta_harris_trump
        ]
    )
)

biggest_delta_trump_harris = get_words_with_deltas(
    speakers[SPEAKER_KEY_TRUMP], speakers[SPEAKER_KEY_HARRIS]
)
print(
    "Words Trump said more often than Harris: "
    + ", ".join(
        [
            word[0] + "(" + str(word[1]) + " times more)"
            for word in biggest_delta_trump_harris
        ]
    )
)
