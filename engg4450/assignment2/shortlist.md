# Assignment 2: shortlist of change requests

Checked on 2026-10-26 against our copy of beets 2.14.1. Five of the seven items were checked: reproduced with a small script, confirmed by reading the code, or found to be not reproducible or already fixed. #4061 and #6770 were not checked in depth, because #6770 needs the Tidal API to be mocked and both were lower priority than the two bugs we selected.

| # | Issue | Type | What the user wants | Status in our code | Effort | Risk | Offline test? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [#7070](https://github.com/beetbox/beets/issues/7070) lyrics: synced LRCLIB lyrics discarded when the LRC ends with a blank line | Bug | Synced lyrics are kept when the LRC text ends with an empty line | **Reproduced**: `LRCLyrics.verify_synced_lyrics` returns `None` for LRC ending in `\r\n\r\n` (it looks only at the last line, `beetsplug/lyrics.py:287`) | S (1-2 h) | Low | Yes, pure function |
| 2 | [#5937](https://github.com/beetbox/beets/issues/5937) embedart: `quality` not used when art is embedded automatically | Bug | The configured JPEG quality is used after `import` / `fetchart`, as it is for `beet embedart` | **Confirmed in code**: `EmbedCoverArtPlugin.process_album` (`beetsplug/embedart.py:277`) calls `art.embed_album` without `quality`, so it defaults to 0 | S (1-2 h) | Low | Yes, with a mock |
| 3 | [#5411](https://github.com/beetbox/beets/issues/5411) export: `--include-keys` does not expand globs as documented | Bug | `beet export -i 'title,mb*'` exports every field starting with `mb` | **Reproduced**: the output has a literal `"mb*"` key with no value | M (3-4 h) | Low-medium | Yes, with a test library |
| 4 | [#4061](https://github.com/beetbox/beets/issues/4061) mbsubmit: sort tracks by disc and track number | Feature | Printed track list of a multi-disc album is in disc/track order | Not checked yet | S-M | Low | Yes |
| 5 | [#6770](https://github.com/beetbox/beets/issues/6770) tidal: `search_limit` is ignored | Bug | Tidal returns at most `search_limit` candidates | Not reproduced (needs Tidal API mocking) | M | Medium | Only with mocks |
| 6 | [#7019](https://github.com/beetbox/beets/issues/7019) modify: `select` writes `ModifyOperation(...)` as the value | Bug | Selected changes store the typed value | **Not reproducible** in 2.14.1 (selected album and its track both get the right value); probably fixed already | - | - | - |
| 7 | [#2836](https://github.com/beetbox/beets/issues/2836) bash completion fails for command names with a hyphen | Bug | Completion works for `foo-bar` commands | **Already fixed** in our code (`beets/ui/commands/completion.py:111`) | - | - | - |

## Recommendation

- **Implement:** #7070 and #5937. Both are real, user-facing bugs; both fixes are small and local; both can be tested without network access or API keys.
- **Backup / stretch:** #5411 (slightly more work, but also offline).
- **Drop:** #7019 and #2836 (not reproducible or already fixed), #6770 (needs API mocking; risky for a one-day sprint).
