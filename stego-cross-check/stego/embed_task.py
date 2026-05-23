#!/usr/bin/env python3
import subprocess
import sys


AUDIO_FILE = ""
SIGN_FILE = ""
OUTPUT_FILE = "marked_cross.wav"
KEY = 13579


def main():
    if not AUDIO_FILE or not SIGN_FILE:
        raise SystemExit("Hay sua cac dong TODO trong embed_task.py truoc khi chay.")
    command = [
        sys.executable,
        "cross_embed.py",
        AUDIO_FILE,
        OUTPUT_FILE,
        "--message-file",
        SIGN_FILE,
        "--key",
        str(KEY),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
