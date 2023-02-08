import datetime
import re
from collections import defaultdict, namedtuple, Counter
from typing import List

import argparse
import srt

parser = argparse.ArgumentParser(description="Generate compact text")

parser.add_argument("-srt", "--input_srt_file", help="Input SRT file", required=True)
parser.add_argument("-txt", "--input_txt_file", help="Edited transcription TXT file", required=True)
parser.add_argument("-m", "--margin", help="Buffer between utterences", default=0, type=int)
parser.add_argument(
    "-g",
    "--greedy",
    help="Greedily selects next word, so runs faster",
    default=True,
    type=bool,
    action=argparse.BooleanOptionalAction,
)

Cut = namedtuple("Cut", ["start", "end"])


def pick_words_greedy(
    words: List[str],
    desired_transcription: str,
) -> List[int]:
    word_index = 0
    n_words = len(words)
    output = []
    for word in re.findall(r"['\w]+", desired_transcription):
        while word_index < n_words and words[word_index].lower() != word.lower():
            word_index += 1
        if word_index == n_words:
            raise ValueError(f"Could not find all words in subtitles. First missing word: {word}")
        output.append(word_index)
        word_index += 1
    return output


def pick_words_brute_force(
    words: List[str],
    desired_transcription: str,
) -> List[int]:
    """Given a list of words from the original transcription and a desired transcription, return a list of
    words' indices that should be selected to achieve the desired transcription.
    """
    word_positions = defaultdict(list)
    for i, word in enumerate(words):
        word_positions[word.lower()].append(i)

    desired_words = [w.lower() for w in re.findall(r"['\w]+", desired_transcription)]
    desired_word_counts = Counter(desired_words)
    for word, count in desired_word_counts.items():
        if count > len(word_positions[word]):
            raise ValueError(f"Could not find all words in subtitles. First missing word: {word}")

    used = [False] * len(words)
    path = []
    best = []
    best_cost = float("inf")

    def backtrack(desired_word_index: int, cost: int, max_branch_factor: int = 3):
        nonlocal best, best_cost, used, path
        if cost > best_cost:
            return
        if desired_word_index == len(desired_words):
            best = path[:]
            best_cost = cost
            return
        word = desired_words[desired_word_index]
        options = [p for p in word_positions[word] if not used[p]]
        current_pos = path[-1] if path else 0
        if len(options) >= max_branch_factor:
            # Only look at the closest options to avoid combinatorial explosion.
            options = sorted(options, key=lambda p: abs(p - current_pos))[:max_branch_factor]
        for option in options:
            option_cost = cost + abs(option - current_pos)
            used[option] = True
            path.append(option)
            backtrack(desired_word_index + 1, option_cost)
            used[option] = False
            path.pop()

    backtrack(0, 0)
    if not best:
        raise RuntimeError("Failed to find words for desired transcription.")
    return best


def compute_cuts(subtitles: List[srt.Subtitle], chosen: List[int], margin: datetime.timedelta) -> List[Cut]:
    """Given a list of subtitles, the list of indices to select, list the timestamp ranges
    that should be cut, while merging segments that are within margin of each other."""
    output = []
    for index in chosen:
        subtitle = subtitles[index]
        start = subtitle.start
        end = subtitle.end
        # print(subtitle.content, start, end)

        # TODO: Should check if margin wouldn't cause overlap with undesired words.
        # TODO: If past word subtitles[index-1] is r"^\'" increase margin by factor? e.g. It's doable
        start -= margin
        end += margin
        if index > 0:
            if subtitles[index - 1].content.startswith("'"):
                start -= margin * 1.1

        if start < datetime.timedelta():
            start = datetime.timedelta()
        if output and output[-1].end >= start and output[-1].start < start:
            output[-1] = Cut(output[-1].start, end)
        else:
            output.append(Cut(start, end))
    return output


def list_cuts(
    subtitles: List[srt.Subtitle],
    desired_transcription: str,
    margin: datetime.timedelta,
    greedy: bool = False,
) -> List[Cut]:
    """Given a list of subtitles and a desired transcription, return a list of cuts
    (start, end) that correspond to segments of the media with the desired transcription. Also
    includes a configurable margin of time before and after each cut."""
    words = [subtitle.content for subtitle in subtitles]
    if greedy:
        chosen_words = pick_words_greedy(words, desired_transcription)
    else:
        chosen_words = pick_words_brute_force(words, desired_transcription)
    return compute_cuts(subtitles, chosen_words, margin)


def main():
    args = parser.parse_args()
    with open(args.input_srt_file, "r") as f:
        subtitles = list(srt.parse(f.read()))
    with open(args.input_txt_file, "r") as f:
        desired_transcription = f.read()

    margin = datetime.timedelta(milliseconds=args.margin)
    print(
        list_cuts(
            subtitles,
            desired_transcription=desired_transcription,
            margin=margin,
            greedy=args.greedy,
        )
    )


if __name__ == "__main__":
    main()
