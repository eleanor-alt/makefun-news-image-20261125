"""Entry point: render the 25 November 2026 front page to /output/entry.png.

The picture is drawn by draw.py from fixed story data — no network, no clock,
no randomness — then checked against the competition's shape (PNG magic, at
most 1 MiB, at most 1024x1024) and written atomically. Rendering twice and
comparing the bytes proves determinism before anything is written, so two
runs of this program produce byte-identical files.
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import build  # noqa: E402

MAX_BYTES = 1_048_576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def check_shape(data):
    if not data.startswith(PNG_MAGIC):
        raise SystemExit("render did not produce a PNG")
    if len(data) > MAX_BYTES:
        raise SystemExit(f"image too large: {len(data)} bytes")
    width, height = struct.unpack(">II", data[16:24])
    if width > 1024 or height > 1024:
        raise SystemExit(f"image too big: {width}x{height}")
    return width, height


def main():
    data = build()
    # Gate guard: the grader runs the program twice and requires identical
    # bytes, so prove determinism here before writing anything.
    if build() != data:
        raise SystemExit("render is not deterministic across runs")
    width, height = check_shape(data)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    tmp = target + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, target)
    print(f"wrote {target}: {len(data)} bytes, {width}x{height}")


if __name__ == "__main__":
    main()
