#!/usr/bin/env python3
from pathlib import Path


WORKDIR = Path.home() / "stego"
RESULT = Path.home() / ".local" / "result" / "cross_check_status.txt"


def main():
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    tokens = []
    if (WORKDIR / "cover.wav").is_file() and (WORKDIR / "cover.wav").stat().st_size > 0:
        tokens.append("PASS_COVER_AVAILABLE")
    if (WORKDIR / "marked_cross.wav").is_file() and (WORKDIR / "marked_cross.wav").stat().st_size > 0:
        tokens.append("PASS_MARKED_CREATED")
    if (WORKDIR / ".valid_checked_done").is_file():
        tokens.append("PASS_VALID_CHECKED")
    if (WORKDIR / ".modified_checked_done").is_file():
        tokens.append("PASS_MODIFIED_CHECKED")
    if (WORKDIR / ".invalid_checked_done").is_file():
        tokens.append("PASS_INVALID_CHECKED")
    RESULT.write_text("\n".join(tokens) + ("\n" if tokens else ""), encoding="utf-8")


if __name__ == "__main__":
    main()
