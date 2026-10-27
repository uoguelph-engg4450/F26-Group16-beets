# Assignment 2: use case descriptions

These go with the use case diagram `diagrams/UC1 beets change requests.png` (source: `beets-a2-usecases.asta`, built by `astah/build.sh`).
UC-1 and UC-2 are the two change requests selected for this sprint. UC-3 is the backup.
The behaviour described under "Main success scenario" is the behaviour **after** the fix. The "Defect" line says what beets 2.14.1 does today.

Primary actor in all three: **Music collector**, a person who manages a music library with the `beet` command-line tool.

---

## UC-1  Fetch synced lyrics ([#7070](https://github.com/beetbox/beets/issues/7070))

| Field | Description |
| --- | --- |
| Scope | beets, `lyrics` plugin, LRCLIB backend |
| Level | User goal |
| Primary actor | Music collector |
| Supporting actor | LRCLIB lyrics service (lrclib.net) |
| Stakeholders and interests | **Music collector:** wants time-synced (LRC) lyrics so players can scroll them with the song. **Maintainers:** want the duration check to keep rejecting lyrics that belong to a longer version of the song. |
| Trigger | The collector runs `beet lyrics <query>`, or imports music with `lyrics.auto: yes` (this extends *Import music*). |
| Preconditions | 1. The `lyrics` plugin is enabled with `synced: yes` and `lrclib` in `sources`. 2. The track is in the library and has a length. 3. LRCLIB is configured as a lyrics source and can be queried for the track. |
| Postconditions (success) | The track's `lyrics` field holds the synced LRC text. If `write` is on, the lyrics are also written to the file tags. |
| Minimal guarantee | Lyrics whose last timestamp is later than the track length are never stored. Existing lyrics are kept unless `force` is used. |
| Defect (beets 2.14.1) | When the LRC text from LRCLIB ends with a blank line (for example `...\r\n\r\n`), beets reads the empty last line, finds no timestamp and discards the synced lyrics. The collector gets plain lyrics or none. |

**Main success scenario**

1. The collector asks beets to fetch lyrics for one or more tracks.
2. For each track, beets searches LRCLIB by artist, title, album and duration.
3. LRCLIB returns one or more candidates with synced and plain lyrics.
4. beets checks each synced text. It ignores trailing blank lines and reads the timestamp of the last line that has text.
5. That timestamp is not later than the track length, so beets accepts the synced lyrics.
6. beets picks the best candidate, prefers synced over plain, and stores the lyrics on the track.
7. beets reports the lyrics as fetched.

**Extensions (alternative flows)**

- 4a. The synced text is empty or only whitespace: beets treats it as "no synced lyrics" and uses the plain lyrics of that candidate (UC continues at 6).
- 5a. The last timestamp is later than the track length: beets rejects the synced lyrics of that candidate and tries the next one. If none is valid, it falls back to plain lyrics.
- 3a. LRCLIB returns no candidates or an error: beets tries the next configured source. If no source has lyrics, it logs "lyrics not found" and the track is unchanged.
- 6a. The track already has lyrics and `force` is off: beets skips the track.

**Special requirements:** works offline in tests (LRCLIB responses are mocked). No new configuration option.

**Acceptance criterion:** an LRCLIB response whose synced text ends with a blank line is stored as synced lyrics, and a synced text whose last timestamp is too late is still rejected.

---

## UC-2  Embed album art at the configured quality ([#5937](https://github.com/beetbox/beets/issues/5937))

| Field | Description |
| --- | --- |
| Scope | beets, `embedart` plugin |
| Level | Subfunction (runs automatically when album art is set) |
| Primary actor | Music collector |
| Supporting actor | Album art sources (through the `fetchart` plugin) |
| Stakeholders and interests | **Music collector:** wants embedded cover art to be resized and compressed the same way every time, to keep files small. **Maintainers:** want the automatic path and the `beet embedart` command to behave the same. |
| Trigger | Album art is set on an album, for example by `fetchart` during `beet import` or by `beet fetchart` (the `art_set` event). This extends *Fetch album art*. |
| Preconditions | 1. `embedart` is enabled with `auto: yes` (default). 2. Writing tags is on (`import.write: yes`). 3. `embedart.maxwidth` and `embedart.quality` are set, for example `maxwidth: 500`, `quality: 75`. 4. ImageMagick or Pillow is installed for resizing. |
| Postconditions (success) | Each eligible track, respecting the if empty and compare_threshold settings, has the album art embedded, resized to `maxwidth` and compressed at `quality`. |
| Minimal guarantee | Only the image tags of the files are changed. The album art file is kept unless `remove_art_file` is on. |
| Defect (beets 2.14.1) | The automatic path calls the embed function without `quality`, so the image is compressed with the tool's default (ImageMagick about 92, Pillow 75). Only `beet embedart` uses the configured value, so the same setting gives different file sizes. |

**Main success scenario**

1. The collector imports an album, or runs `beet fetchart`, with `fetchart` and `embedart` enabled.
2. `fetchart` finds cover art and sets it on the album.
3. beets sends the `art_set` event; `embedart` receives it.
4. `embedart` reads `maxwidth`, `compare_threshold`, `ifempty` and `quality` from its configuration.
5. `embedart` resizes the image to `maxwidth` at the configured `quality` and embeds it in each eligible track, respecting the `ifempty` and `compare_threshold` settings.
6. If `remove_art_file` is on, `embedart` deletes the album art file.

**Extensions (alternative flows)**

- 3a. `auto` is off or writing is off: nothing is embedded; the art file stays on disk.
- 5a. `maxwidth` is 0: the image is embedded as is and `quality` has no effect (as documented).
- 5b. `ifempty` is on and a track already has art: that track is skipped.
- 5c. `compare_threshold` is set and the new art is too different from the existing art: that track is skipped and a message is logged.
- 5d. No image tool is installed: `maxwidth` is ignored with a warning and the original image is embedded.

**Special requirements:** no new configuration option; the documented `quality` option must apply on both paths.

**Acceptance criterion:** with `quality: 75`, art embedded automatically is passed to the resizer with quality 75, the same as `beet embedart -y`.

---

## UC-3 (backup)  Export selected fields ([#5411](https://github.com/beetbox/beets/issues/5411))

| Field | Description |
| --- | --- |
| Level | User goal |
| Primary actor | Music collector |
| Trigger | `beet export -i 'title,mb*' <query>` |
| Preconditions | The `export` plugin is enabled. |
| Postconditions | The output has `title` and every field whose name starts with `mb` (for example `mb_trackid`, `mb_albumid`). |
| Defect (beets 2.14.1) | The pattern is not expanded. The output has a literal key `"mb*"` with an empty value. |

**Main success scenario:** 1. The collector runs the export command with a glob in `--include-keys`. 2. beets matches each pattern against the item's field names. 3. beets writes the matching fields in the chosen format (JSON, CSV, XML). **Extension:** 2a. A pattern matches no field: it is left out of the output.
