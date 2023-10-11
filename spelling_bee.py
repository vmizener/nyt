#!/usr/bin/env python3
import argparse
import textwrap

WORD_DICT = "/usr/share/dict/words"

# Note that you can also try
# `dict -s -re -m '^[{chars}]*$' -f | cut -f4 | grep {key_char} | awk 'length >= {min_len}'`


def get_words(chars, min_length):
    words = []
    charset = set(chars)
    with open(WORD_DICT, "r") as fh:
        for line in fh.readlines():
            word = line.strip()
            if len(word) < min_length:
                continue
            wordset = set(word)
            if chars[0] in wordset and len(wordset - charset) == 0:
                words.append(word)
    return words


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Solver for the NYT spelling bee.

            Note that only a curated set of "common words" are accepted by the bee, so some returned words may be rejected.
            """
        ),
    )
    parser.add_argument(
        "chars",
        type=str,
        help="Legal characters in word.  First character must be included.",
    )
    parser.add_argument(
        "min_len",
        type=int,
        nargs="?",
        default=4,
        help="Minimum word length.  Default: 4",
    )
    args = parser.parse_args()
    for word in get_words(args.chars, args.min_len):
        print(word)
