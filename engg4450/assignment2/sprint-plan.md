# Assignment 2: sprint plan (A2 Sprint 1)

Jira: project **KAN** (ENGG4450-Group16) on `4450-group16.atlassian.net`, sprint **A2 Sprint 1**, Oct 26 to Oct 27, 2026, 11:59 pm.
Sprint goal: fix #7070 and #5937 with tests, merge both into `phase-2` of `uoguelph-engg4450/F26-Group16-beets` from members' own accounts, then merge `phase-2` into `main`, pass acceptance tests CAT-1 to CAT-6, and submit the report.

## Process model: Scrum, one short sprint

We use Scrum because the work is a small, prioritised backlog of change requests and the customer (PO) accepts each item against written criteria.
The sprint is one day long, so the events are short:

| Event | When | Who | Output |
| --- | --- | --- | --- |
| Backlog refinement | before the sprint | SM, PO | shortlist of 7 issues, each reproduced or checked (`shortlist.md`) |
| Sprint planning | Oct 26 | whole team | 2 stories selected, estimates, risks, allocation (this file, Jira) |
| Daily check-in | Oct 26 evening, Oct 27 midday | whole team, 10 min | board updated, blockers raised |
| Sprint review | Oct 27 afternoon | PO + team | acceptance tests run on `phase-2`, stories accepted |
| Release check | Oct 27, after `phase-2` is merged into `main` | tester, SM | full test suite and acceptance tests re-run on `main`; release commit recorded in the report |
| Retrospective | Oct 27 | whole team, 10 min | what went well / what to change (report) |

Board columns: To Do → In Progress → Done. A story is **Done** when its PR is merged into `phase-2`, the full test suite passes, its acceptance tests pass and the PO has accepted it. The sprint is finished when `phase-2` has been merged into `main` and the acceptance tests pass again on `main`.

## Roles and allocation

| Member | Sprint role | Jira items | GitHub |
| --- | --- | --- | --- |
| Abdul Moeiz Ahmed | Product Owner: accepts stories, runs the sprint review; owns the use case diagram and descriptions | KAN-10, KAN-14 | @abdulma3 |
| Zaryan Syed | Scrum Master: board, blockers, planning and retro; process section of the report | KAN-9, KAN-12, KAN-15 | @syedzar |
| Shailen Naik | Developer, #7070 | KAN-6, KAN-16, KAN-17 | @ShailenN1 |
| Hasan Shariq | Reviewer/tester, #7070: reviews and merges the PR; owns the customer acceptance tests | KAN-11, KAN-18 | @ShariqHas |
| Abdul Hadi | Developer, #5937 | KAN-7, KAN-19, KAN-20 | @abdulhadi-1 |
| Faraz Afnan Haque | Reviewer/tester, #5937: reviews and merges the PR; assembles the report | KAN-13, KAN-21 | @FarazAfnan |

Everyone makes at least one commit from their own GitHub account: the fix (developers), the merge and the `acceptance/` folder (reviewers), the use case files (PO), and the sprint and process notes (SM).

## Selected items, estimates and risks

| Jira | Item | Points | Effort | Risk | Mitigation |
| --- | --- | --- | --- | --- | --- |
| KAN-6 | #7070 synced LRCLIB lyrics dropped when the LRC ends with a blank line | 2 | 1–2 h | Low: one function; could also accept lyrics it should reject | regression tests for both cases (CAT-1, CAT-2); full suite run |
| KAN-7 | #5937 embedart ignores `quality` when embedding automatically | 2 | 1–2 h | Low: one call; changelog conflict with KAN-6 | test with a mock plus end-to-end CAT-4/5; merge order documented |
| KAN-8 | (backup) #5411 `export --include-keys` globs | 3 | 3–4 h | Low–medium | only pulled in if KAN-6 or KAN-7 is blocked |
| KAN-10 | use case diagram and descriptions | 3 | 2 h | Low | draft already built in Astah |
| KAN-11 | customer acceptance tests | 2 | 1 h | Low | automated runner, no network needed |
| KAN-12 | process, estimates, risks, allocation write-up | 2 | 1 h | Low | this file |
| KAN-13 | report (max 20 pages) | 3 | 3 h | Medium: deadline | start sections in parallel on Oct 26 |
| KAN-14 | sprint review | 1 | 30 min | Low | — |
| KAN-15 | planning, check-ins and retro | 1 | 30 min | Low | — |
| | **Sprint total** | **18** | | | |

The 18 points are the nine sprint items: KAN-6 (2) + KAN-7 (2) + KAN-9 (2, already done) + KAN-10 (3) + KAN-11 (2) + KAN-12 (2) + KAN-13 (3) + KAN-14 (1) + KAN-15 (1). The backup KAN-8 (3) stays in the product backlog and is not counted. The same total shows in Jira for A2 Sprint 1.

Team-level risks:

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| A member cannot push to the class repository | Possible | Their commits are not counted (GitHub is 10%) | everyone checks access on day 1; the TA adds anyone missing | SM |
| Unclear which version is the release | Possible | TA marks the wrong version | all PRs go into `phase-2`; one final PR merges it into `main`; the report names the release commit | SM |
| Both PRs edit `docs/changelog.rst` | Certain | merge conflict on the second PR | keep both entries; tested | reviewers |
| Deadline (one day) | Medium | late submission | small stories, patches and tests already prepared | whole team |

## Setup checklist for each member

1. Log in to `4450-group16.atlassian.net` and open board **KAN → A2 Sprint 1**. Check that your items are assigned to you.
2. Make sure your GitHub account can push to `uoguelph-engg4450/F26-Group16-beets`.
3. Clone the repo, create a virtual environment and install beets with its test tools:
   `pip install -e . pytest requests-mock pillow`
4. Run `python -m pytest test/plugins/test_lyrics.py test/plugins/test_embedart.py -q` to check your setup.
5. Branch from `phase-2` and open your PR into `phase-2`. Developers: branch, make the fix, test, commit, PR. Reviewers: review on GitHub, run the tests, merge.
6. Move your Jira item to In Progress when you start and to Done when it meets the definition of done. Start your commit message and PR title with the Jira key (for example `KAN-6`). This makes the link clear in GitHub, and Jira shows the commits in its Development panel if the GitHub for Jira app is connected.
