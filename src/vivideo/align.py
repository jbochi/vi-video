import datetime
import re
from collections import defaultdict, namedtuple, Counter
from typing import List

from vivideo.transcribe import WordAndSpan

Cut = namedtuple("Cut", ["start", "end"])

WORD_PATTERN = re.compile(r"[^\s.,]+")


def words_in_transcription(desired_transcription):
    return [w.lower() for w in WORD_PATTERN.findall(desired_transcription)]


def pick_words_greedy(
    words: List[str],
    desired_transcription: str,
) -> List[int]:
    word_index = 0
    n_words = len(words)
    output = []
    for word in words_in_transcription(desired_transcription):
        while word_index < n_words and words[word_index].lower() != word:
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

    desired_words = words_in_transcription(desired_transcription)
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


def compute_cuts(word_spans: List[WordAndSpan], chosen: List[int], padding: datetime.timedelta) -> List[Cut]:
    """Given a list of subtitles, the list of indices to select, list the timestamp ranges
    that should be cut, while merging segments that are within margin of each other."""
    output = []
    for index in chosen:
        word_span = word_spans[index]
        start = word_span.start
        end = word_span.end

        # avoid overlap with previous and next words
        start = max(
            start - padding, datetime.timedelta(0) if index == 0 else (start + word_spans[index - 1].end) / 2.0
        )
        end = min(
            end + padding, end + padding if index + 1 == len(word_spans) else (end + word_spans[index + 1].start) / 2.0
        )

        if output and output[-1].end >= start and output[-1].start < start:
            output[-1] = Cut(output[-1].start, end)
        else:
            output.append(Cut(start, end))
    return output


def list_cuts(
    transcription: List[WordAndSpan],
    desired_transcription: str,
    padding: datetime.timedelta,
    greedy: bool = False,
) -> List[Cut]:
    """Given a list of subtitles and a desired transcription, return a list of cuts
    (start, end) that correspond to segments of the media with the desired transcription. Also
    includes a configurable margin of time before and after each cut."""
    words = [word.word for word in transcription]
    if greedy:
        chosen_words = pick_words_greedy(words, desired_transcription)
    else:
        chosen_words = pick_words_brute_force(words, desired_transcription)
    return compute_cuts(transcription, chosen_words, padding)
