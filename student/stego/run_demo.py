#!/usr/bin/env python3
import subprocess
import sys


COMMANDS = [
    ["cross_embed.py", "cover.wav", "marked_cross.wav", "--message", "cross check demo", "--key", "13579"],
    ["cross_verify.py", "marked_cross.wav", "--key", "13579"],
    ["attack.py", "marked_cross.wav", "light_modified.wav", "--type", "crop", "--level", "light"],
    ["cross_verify.py", "light_modified.wav", "--key", "13579"],
    ["attack.py", "marked_cross.wav", "destroyed.wav", "--type", "replace", "--level", "heavy"],
    ["cross_verify.py", "destroyed.wav", "--key", "13579"],
]


def main():
    for command in COMMANDS:
        print("$", " ".join(["python3", *command]))
        subprocess.run([sys.executable, *command], check=True)


if __name__ == "__main__":
    main()
