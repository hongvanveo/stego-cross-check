#!/usr/bin/env python3
import subprocess
import sys


AUDIO_FILE = ""
SIGN_FILE = ""
KEY = 13579


def main():
    if not AUDIO_FILE or not SIGN_FILE:
        raise SystemExit("Hay sua cac dong TODO trong verify_task.py truoc khi chay.")
    command = [
        sys.executable,
        "cross_verify.py",
        AUDIO_FILE,
        "--sign-file",
        SIGN_FILE,
        "--key",
        str(KEY),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
