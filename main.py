#!/usr/bin/env python3
"""news-image-20261125 entrypoint.

Copies the pre-rendered front page (entry.png, built at authoring time
by render_image.py) to /output/entry.png, byte for byte.

Standard library only. No network, no randomness: running this twice
produces identical bytes.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
DEST_DIR = "/output"
DEST = os.path.join(DEST_DIR, "entry.png")
BLOCK = 16384


def _digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            piece = fh.read(BLOCK)
            if not piece:
                break
            h.update(piece)
    return h.hexdigest()


def main():
    if not os.path.isfile(SOURCE):
        sys.stderr.write("entry.png not found next to main.py\n")
        return 1
    os.makedirs(DEST_DIR, exist_ok=True)
    total = 0
    with open(SOURCE, "rb") as src, open(DEST, "wb") as dst:
        while True:
            chunk = src.read(BLOCK)
            if not chunk:
                break
            dst.write(chunk)
            total += len(chunk)
        dst.flush()
        os.fsync(dst.fileno())
    if os.path.getsize(DEST) != total or total == 0:
        sys.stderr.write("size mismatch after copy\n")
        return 1
    if _digest(SOURCE) != _digest(DEST):
        sys.stderr.write("sha256 mismatch after copy\n")
        return 1
    print("wrote %s (%d bytes)" % (DEST, total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
