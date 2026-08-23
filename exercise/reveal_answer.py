"""Reveal the exercise answer.

Run this only after you have committed to an answer in writing.

    python3 exercise/reveal_answer.py
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

ANSWER = Path(__file__).resolve().parent / "data" / "ANSWER.txt"


def main() -> None:
    lines = ANSWER.read_text(encoding="utf-8").splitlines()
    payload = [line for line in lines
               if len(line) > 40 and re.fullmatch(r"[A-Za-z0-9+/=]+", line)]
    print(base64.b64decode("".join(payload)).decode("utf-8"))


if __name__ == "__main__":
    main()
