import datetime
import heapq
import re
from collections import defaultdict, namedtuple, Counter
from typing import List

import argparse
import srt

parser = argparse.ArgumentParser(description="Generate compact text")

parser.add_argument("-srt", "--input_srt_file", help="Input SRT file", required=True)
parser.add_argument(
    "-txt", "--input_txt_file", help="Edited transcription TXT file", required=True
)
parser.add_argument(
    "-m", "--margin", help="Buffer between utterences", default=0, type=int
)
parser.add_argument(
    "-g",
    "--greedy",
    help="Greedily selects next word, so runs faster",
    default=True,
    type=bool,
    action=argparse.BooleanOptionalAction,
)

Cut = namedtuple("Cut", ["start", "end"])
SearchNode = namedtuple("SearchNode", ["cost", "neg_length", "path"])


def pick_words_greedy(
    words: List[str],
    desired_transcription: str,
    greedy: bool = True,
) -> List[int]:
    word_index = 0
    n_words = len(words)
    output = []
    for word in re.findall(r"['\w]+", desired_transcription):
        while word_index < n_words and words[word_index].lower() != word.lower():
            word_index += 1
        if word_index == n_words:
            raise ValueError(
                f"Could not find all words in subtitles. First missing word: {word}"
            )
        output.append(word_index)
        word_index += 1
    return output


def pick_words(
    words: List[str],
    desired_transcription: str,
    greedy: bool = True,
) -> List[int]:
    """Given a list of words from the original transcription and a desired transcription, return a list of
    words' indices that should be selected to achieve the desired transcription.
    """
    if greedy:
        return pick_words_greedy(words, desired_transcription, greedy=greedy)

    word_positions = defaultdict(list)
    for i, word in enumerate(words):
        word_positions[word.lower()].append(i)

    desired_words = [w.lower() for w in re.findall(r"['\w]+", desired_transcription)]
    desired_word_counts = Counter(desired_words)
    for word, count in desired_word_counts.items():
        if count > len(word_positions[word]):
            raise ValueError(
                f"Could not find all words in subtitles. First missing word: {word}"
            )

    heap = []
    heapq.heappush(heap, SearchNode(cost=0, neg_length=0, path=[]))
    while heap:
        alternative = heapq.heappop(heap)
        if len(alternative.path) == len(desired_words):
            return alternative.path
        word = desired_words[len(alternative.path)]
        used = set(alternative.path)

        for position in word_positions[word]:
            if position in used:
                continue
            new_path = alternative.path + [position]
            current_position = alternative.path[-1] if alternative.path else position - 1
            distance = abs(position - current_position)
            new_cost = alternative.cost + distance - 1
            heapq.heappush(
                heap,
                SearchNode(cost=new_cost, neg_length=-len(new_path), path=new_path),
            )

    raise ValueError(
        "Could not find a set of words that would match the desired transcription."
    )


def compute_cuts(
    subtitles: List[srt.Subtitle], chosen: List[int], margin: datetime.timedelta
) -> List[Cut]:
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
    chosen_words = pick_words(words, desired_transcription, greedy=greedy)
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
