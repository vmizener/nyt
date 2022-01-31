#!/usr/bin/env python3
import argparse
import collections
import string
import textwrap

src = "./wordle_words.txt"


class Wordle:
    @staticmethod
    def dump_help(silent=False):
        msg = textwrap.dedent(
            """
            This is an interactive solver utility for "Wordle", a popular word game.

            This utility helps by providing a list of legal words, given information from prior guesses.

            Simply input a guess at the ">" prompt, followed by a validation string indicating feedback to the guess at the "?" prompt.  The utility will then provide a list of potential guesses in response.

            A validation string indicates which letters of a guess are green, yellow, or grey, based on position.

            E.g. after submitting the guess "earth", a validation string of "gy..." indicates "e" as green, "a" as yellow, and "r", "t", and "h" as grey.

            At any time, a user may submit "?" to receive the list of potential guesses.  This list is given automatically once the number of potential options is below a fixed threshold.

            Note that the solver does not respect the game's rule of restricting input to defined words.


            For reference, the following inputs are supported:
                ?     Print a list of potential guesses, given prior guesses.
                ??    Print this help message.
                ^C    Quit the game.
                ^D    Reset the game, forgetting any prior guesses.
            """
        )

        if not silent:
            print(msg)
        return msg

    def __init__(self, word_len=5, max_guesses=6):
        self.word_len = word_len
        self.max_guesses = max_guesses
        self.reset()

    @property
    def words(self):
        return self._words

    def reset(self):
        self._words = set()
        with open(src, "r") as fh:
            for line in fh.readlines():
                word = line.strip()
                if (
                    len(word) != self.word_len
                    or len(set(word) - set(string.ascii_lowercase)) > 0
                ):
                    continue
                self._words.add(word)

    def dump_options(self, cols=5):
        for idx, w in enumerate(sorted(self.words)):
            print(w, end=" ")
            if (idx + 1) % cols == 0:
                print()
        print()

    def play(self):
        while True:
            try:
                self.filter(*self.prompt())
            except EOFError:
                print()
                print("Game reset.")
                self.reset()
            except KeyboardInterrupt:
                break

    def prompt(self, dump_threshold=25):
        if len(self.words) == 0:
            print("No legal words remaining.  Input ^C to quit, or ^D to reset.")
        elif len(self.words) <= dump_threshold:
            self.dump_options()
        help_msg = "Enter '?' for word list, or '??' for detailed help.\nInput '^C' to quit, or '^D' to reset."
        # Word input
        while True:
            word = input("> ")
            if word == "?":
                self.dump_options()
            elif word == "??":
                self.dump_help()
            elif len(word) != self.word_len:
                print(f"Guess must be {self.word_len} characters")
                print(help_msg)
            elif len(set(word) - set(string.ascii_lowercase)) > 0:
                print("Guess must contain only lowercase letters")
                print(help_msg)
            else:
                break
        # Validation input
        while True:
            validation = input("? ")
            if validation == "?":
                print("ok")
            elif word == "??":
                self.dump_help()
            elif len(validation) != self.word_len:
                print(f"Validation string must be {self.word_len} characters")
                print(help_msg)
            elif len(set(validation) - set("gy.")) > 0:
                print("Validation string must contain only 'g', 'y', or '.' characters")
                print(help_msg)
            else:
                break
        return word, validation

    def filter(self, word, validation_string):
        missing = set()
        members = collections.Counter()
        pos_info = {}
        for idx, (c, t) in enumerate(zip(word, validation_string)):
            if t == ".":
                if any([c in key for key in pos_info.values()]):
                    # Don't add to missing if it's seen elsewhere
                    continue
                missing.add(c)
            elif t == "y":
                members[c] += 1
                pos_info.setdefault(idx, f"-{c}")
            else:
                members[c] += 1
                pos_info.setdefault(idx, f"{c}")
        illegal_words = set()
        for option in self.words:
            if len(set(option) & missing) > 0:
                # Contains missing characters
                illegal_words.add(option)
                continue
            for idx, info in pos_info.items():
                c = option[idx]
                if "-" in info:
                    if c == info[1]:
                        # Character in illegal position
                        illegal_words.add(option)
                        break
                    continue
                elif c != info:
                    # Character is incorrect
                    illegal_words.add(option)
                    break
            else:
                counts = collections.Counter(option)
                for member_char, count in members.items():
                    if counts[member_char] < count:
                        # Missing minimum count of known characters
                        illegal_words.add(option)
                        break
        self._words -= illegal_words


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(Wordle.dump_help(silent=True)),
    )
    parser.add_argument(
        "-l",
        "--word_len",
        type=int,
        metavar="LEN",
        default=5,
        help="length of words (default: 5)",
    )
    parser.add_argument(
        "-g",
        "--max_guesses",
        type=int,
        metavar="NUM",
        default=6,
        help="max number of guesses (default: 6)",
    )
    args = parser.parse_args()
    Wordle(word_len=args.word_len, max_guesses=args.max_guesses).play()
