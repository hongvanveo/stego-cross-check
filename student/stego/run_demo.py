#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys


COMMANDS = [
    ["cross_embed.py", "cover.wav", "marked_cross.wav", "--message-file", "message.txt", "--key", "13579"],
    ["cross_verify.py", "marked_cross.wav", "--sign-file", "message.txt", "--key", "13579"],
    ["attack.py", "marked_cross.wav", "light_modified.wav", "--type", "crop", "--level", "light"],
    ["cross_verify.py", "light_modified.wav", "--sign-file", "message.txt", "--key", "13579"],
    ["attack.py", "marked_cross.wav", "destroyed.wav", "--type", "replace", "--level", "heavy"],
    ["cross_verify.py", "destroyed.wav", "--sign-file", "message.txt", "--key", "13579"],
]


def main():
    Path("message.txt").write_text("cross check demo\n", encoding="utf-8")
    for command in COMMANDS:
        print("$", " ".join(["python3", *command]))
        subprocess.run([sys.executable, *command], check=True)


if __name__ == "__main__":
    main()
