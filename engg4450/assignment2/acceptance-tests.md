# Assignment 2: customer acceptance tests

The tests are written from the music collector's point of view (see `use-cases.md`). Each one runs the real `beet` command on a fresh library.
The automated version is `acceptance/run_acceptance.py`. It needs no network access:

- LRCLIB is replaced by a fixed answer, so the result does not depend on what the live site returns that day;
- the cover art comes from a `cover.jpg` in the album folder, which is how many users already keep their art.

```bash
pip install requests-mock pillow
python engg4450/assignment2/acceptance/run_acceptance.py
```

Exit code 0 means every acceptance test passed. `--src <folder>` runs the tests against another copy of beets.

## UC-1 Fetch synced lyrics (#7070)

Common setup: the `lyrics` plugin with `sources: [lrclib]` and `synced: yes`, and one imported track.

| ID | Given | When | Then |
| --- | --- | --- | --- |
| CAT-1 | LRCLIB has synced lyrics for the track that end with a blank line (`[00:00.00] first line\r\n\r\n`) | the collector runs `beet lyrics --force` | the track's lyrics are the **synced** text `[00:00.00] first line` |
| CAT-2 | LRCLIB's synced lyrics end at 59:00, longer than the track, and also end with a blank line | the collector runs `beet lyrics --force` | the synced lyrics are rejected and the **plain** lyrics `plain words` are stored |
| CAT-3 (regression) | LRCLIB has synced lyrics with no blank line at the end | the collector runs `beet lyrics --force` | the synced text is stored, as before the change |

`--force` is used only because the sample track already has plain lyrics in its tags.

## UC-2 Embed album art at the configured quality (#5937)

Common setup: `fetchart` (source `filesystem`) and `embedart` with `auto: yes` and `maxwidth: 200`. The import uses `copy: yes` and `write: yes`. The album folder holds one track and a 500×490 `cover.jpg`.

| ID | Given | When | Then |
| --- | --- | --- | --- |
| CAT-4 | `embedart.quality` is 20 in one library and 95 in another | the collector runs `beet import` on the same album in each | the art embedded at quality 20 is smaller than the art embedded at quality 95 |
| CAT-5 | `embedart.quality: 20` | the collector imports the album (art embedded automatically), and in a second library embeds the same cover with `beet embedart -y -f cover.jpg` | both embedded images have the same size in bytes and the same dimensions |
| CAT-6 (regression) | `embedart.maxwidth: 200` | the collector imports the album | the embedded image is 200 px wide |

## Results (run on 2026-10-26, Windows 11, Python 3.14.7, Pillow resizer)

| Test | `origin/main` (no fix) | #7070 only | #5937 only | both fixes |
| --- | --- | --- | --- | --- |
| CAT-1 | **FAIL**: stored `first line` (plain) | PASS | **FAIL** | PASS |
| CAT-2 | PASS | PASS | PASS | PASS |
| CAT-3 | PASS | PASS | PASS | PASS |
| CAT-4 | **FAIL**: 12114 bytes at both quality 20 and 95 | **FAIL** | PASS: 4895 vs 26693 bytes | PASS |
| CAT-5 | **FAIL**: import 12114 bytes, `beet embedart` 4895 bytes | **FAIL** | PASS: 4895 = 4895 bytes | PASS |
| CAT-6 | PASS | PASS | PASS | PASS |
| Total | 3 / 6 | 4 / 6 | 5 / 6 | **6 / 6** |

On the unchanged code, each change request's own tests fail, and they pass once that fix is applied. The regression tests (CAT-2, CAT-3, CAT-6) pass on every version.

## Manual demo for the customer (optional)

1. In a scratch folder, create `config.yaml` with the UC-2 setup above and `quality: 20`, and set `BEETSDIR` to that folder.
2. Put an MP3 and a large `cover.jpg` in `album/`, then run `beet import -A -q album`.
3. Run `beet list -p`. Open the file in a tag editor, or run `python -c "from mediafile import MediaFile; import sys; print(len(MediaFile(sys.argv[1]).images[0].data))" <path>`.
4. Change `quality` to 95, run steps 2–3 again in a new folder, and compare the sizes. Before the fix they are the same; after the fix the quality 95 image is larger.
