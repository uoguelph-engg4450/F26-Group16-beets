"""Customer acceptance tests for #7070 (synced lyrics) and #5937 (embedart quality).

Each test sets up a fresh library in a temporary folder and drives beets the
way a user would: ``beet import``, ``beet lyrics``, ``beet embedart`` and
``beet list``. Only LRCLIB is replaced by a local answer (see beet_stub.py);
album art comes from a cover.jpg next to the music, as it would for a user.

usage:
    python run_acceptance.py [--src <beets source folder>]

Run it from a checkout of the team repository (the default --src is the
repository root). Needs requests-mock and Pillow:
    pip install requests-mock pillow
Exit code 0 means every acceptance test passed.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUB = HERE / "beet_stub.py"


class Library:
    """A throwaway beets setup: config, library database and music folder."""

    def __init__(self, src: Path, config: str) -> None:
        self.src = src
        self.root = Path(tempfile.mkdtemp(prefix="a2-cat-"))
        self.music = self.root / "music" / "album"
        self.music.mkdir(parents=True)
        (self.root / "config").mkdir()
        lib = (self.root / "lib").as_posix()
        db = (self.root / "library.db").as_posix()
        (self.root / "config" / "config.yaml").write_text(
            f"directory: {lib}\nlibrary: {db}\n{config}", encoding="utf-8"
        )
        shutil.copy(src / "test" / "rsrc" / "full.mp3", self.music / "01.mp3")

    def beet(self, *args: str, lrclib: list | None = None) -> str:
        env = dict(os.environ)
        env["BEETSDIR"] = str(self.root / "config")
        env["PYTHONPATH"] = str(self.src)
        env["PYTHONIOENCODING"] = "utf-8"
        env.pop("A2_LRCLIB_STUB", None)
        if lrclib is not None:
            stub = self.root / "lrclib.json"
            stub.write_text(json.dumps(lrclib), encoding="utf-8")
            env["A2_LRCLIB_STUB"] = str(stub)
        out = subprocess.run(
            [sys.executable, str(STUB), *args],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if out.returncode:
            raise RuntimeError(f"beet {' '.join(args)} failed:\n{out.stderr}")
        return out.stdout

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


# --- #7070 synced lyrics -----------------------------------------------------

LYRICS_CONFIG = """\
import: {copy: no, write: no}
plugins: [lyrics]
lyrics: {sources: [lrclib], synced: yes, auto: no}
"""


def fetch_lyrics(src: Path, synced: str | None, plain: str | None) -> str:
    """Import one track, run ``beet lyrics`` and return the stored lyrics."""
    lib = Library(src, LYRICS_CONFIG)
    try:
        lib.beet("import", "-A", "-q", str(lib.music))
        length = _seconds(lib.beet("list", "-f", "$length").strip())
        candidate = {
            "id": 1,
            "instrumental": False,
            "duration": length,
            "syncedLyrics": synced,
            "plainLyrics": plain,
        }
        # --force: the sample track already has plain lyrics in its tags
        lib.beet("lyrics", "--force", lrclib=[candidate])
        return lib.beet("list", "-f", "$lyrics").rstrip("\n")
    finally:
        lib.cleanup()


def _seconds(text: str) -> float:
    """Turn beets' ``m:ss`` length display into seconds."""
    minutes, seconds = text.split(":")
    return 60 * int(minutes) + float(seconds)


def cat_1(src: Path) -> tuple[bool, str]:
    """Synced lyrics that end with a blank line are saved as synced lyrics."""
    stored = fetch_lyrics(src, "[00:00.00] first line\r\n\r\n", "first line")
    return stored.startswith("[00:00.00]"), f"stored lyrics: {stored!r}"


def cat_2(src: Path) -> tuple[bool, str]:
    """Synced lyrics that run past the end of the track are still rejected."""
    stored = fetch_lyrics(src, "[59:00.00] too late\n\n", "plain words")
    return stored == "plain words", f"stored lyrics: {stored!r}"


def cat_3(src: Path) -> tuple[bool, str]:
    """Synced lyrics without a trailing blank line still work (regression)."""
    stored = fetch_lyrics(src, "[00:00.00] first line", "first line")
    return stored == "[00:00.00] first line", f"stored lyrics: {stored!r}"


# --- #5937 embedart quality --------------------------------------------------


def embed_config(quality: int, auto: bool = True) -> str:
    return f"""\
import: {{copy: yes, write: yes}}
plugins: [fetchart, embedart]
fetchart: {{sources: [filesystem], auto: {"yes" if auto else "no"}}}
embedart: {{auto: yes, maxwidth: 200, quality: {quality}}}
"""


def embedded_image(lib: Library) -> tuple[int, tuple[int, int]]:
    """Return (size in bytes, (width, height)) of the art embedded in the track."""
    from mediafile import MediaFile
    from PIL import Image

    track = lib.beet("list", "-p").strip()  # the copy inside the library
    images = MediaFile(track).images
    if not images:
        return 0, (0, 0)
    data = images[0].data
    return len(data), Image.open(io.BytesIO(data)).size


def import_with_art(src: Path, quality: int) -> tuple[int, tuple[int, int]]:
    """Import an album with a cover.jpg; art is fetched and embedded on import."""
    lib = Library(src, embed_config(quality))
    try:
        shutil.copy(
            src / "test" / "rsrc" / "abbey-similar.jpg", lib.music / "cover.jpg"
        )
        lib.beet("import", "-A", "-q", str(lib.music))
        return embedded_image(lib)
    finally:
        lib.cleanup()


def embed_by_command(src: Path, quality: int) -> tuple[int, tuple[int, int]]:
    """Embed the same cover with the ``beet embedart`` command instead."""
    lib = Library(src, embed_config(quality, auto=False))
    try:
        cover = lib.root / "cover.jpg"
        shutil.copy(src / "test" / "rsrc" / "abbey-similar.jpg", cover)
        lib.beet("import", "-A", "-q", str(lib.music))
        lib.beet("embedart", "-y", "-f", str(cover))
        return embedded_image(lib)
    finally:
        lib.cleanup()


def cat_4(src: Path) -> tuple[bool, str]:
    """A lower quality setting gives a smaller embedded image on import."""
    low, _ = import_with_art(src, 20)
    high, _ = import_with_art(src, 95)
    return 0 < low < high, f"quality 20: {low} bytes, quality 95: {high} bytes"


def cat_5(src: Path) -> tuple[bool, str]:
    """Art embedded on import is the same as art embedded with ``beet embedart``."""
    auto, auto_size = import_with_art(src, 20)
    manual, manual_size = embed_by_command(src, 20)
    detail = f"import: {auto} bytes {auto_size}, beet embedart: {manual} bytes"
    return auto > 0 and auto == manual, f"{detail} {manual_size}"


def cat_6(src: Path) -> tuple[bool, str]:
    """``maxwidth`` is still applied to art embedded on import (regression)."""
    size, (width, _) = import_with_art(src, 20)
    return size > 0 and width == 200, f"embedded width: {width}px"


TESTS = [
    ("CAT-1", "#7070", cat_1),
    ("CAT-2", "#7070", cat_2),
    ("CAT-3", "#7070", cat_3),
    ("CAT-4", "#5937", cat_4),
    ("CAT-5", "#5937", cat_5),
    ("CAT-6", "#5937", cat_6),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--src",
        type=Path,
        default=HERE.parents[2],
        help="beets source folder to test (default: the repository root)",
    )
    src = parser.parse_args().src.resolve()
    sys.path.insert(0, str(src))
    print(f"beets source: {src}")

    failed = 0
    for test_id, issue, test in TESTS:
        try:
            ok, detail = test(src)
        except Exception as exc:  # report and keep going
            ok, detail = False, f"error: {exc}"
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {test_id} {issue}  {test.__doc__}")
        print(f"      {detail}")

    print(f"\n{len(TESTS) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
