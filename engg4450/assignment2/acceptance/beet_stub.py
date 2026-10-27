"""Run the ``beet`` command, optionally with LRCLIB answered from a local file.

usage: python beet_stub.py <beet arguments>

If the environment variable ``A2_LRCLIB_STUB`` names a JSON file, every
LRCLIB search returns the contents of that file and every other web request
fails. This keeps the lyrics acceptance tests offline and repeatable.
"""

import json
import os
import sys

from beets.ui import main


def run() -> None:
    stub = os.environ.get("A2_LRCLIB_STUB")
    if not stub:
        main(sys.argv[1:])
        return

    import requests_mock

    from beetsplug.lyrics import LRCLib

    with open(stub, encoding="utf-8") as f:
        candidates = json.load(f)

    with requests_mock.Mocker() as mock:
        mock.get(LRCLib.GET_URL, status_code=404)
        mock.get(LRCLib.SEARCH_URL, json=candidates)
        main(sys.argv[1:])


if __name__ == "__main__":
    run()
