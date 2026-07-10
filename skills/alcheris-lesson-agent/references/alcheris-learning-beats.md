# Alcheris Learning Beats (Guided Flow)

Alcheris is a self-study product. Many learners open lessons on a phone; desktop learners
can also toggle **guided flow** (the Layers button in the player header) to step through
the same one-column, block-by-block path. Both experiences run the same learning-beats
engine - so beat quality decides both, not just the mobile view.

A desktop page has two panels (left teaches, right acts); phones and guided desktop have
one column. Alcheris bridges the two with **learning beats**.

A learning beat is a small teaching unit, one layer above blocks:

```text
setup / explanation  ->  model / example  ->  practice  ->  feedback / summary
```

On mobile (and in desktop guided flow), the lesson is rendered as a sequence of beats,
not as two panels. The agent that authors the lesson usually does not set beats by hand -
the app auto-generates them. But **beat quality is decided by authoring choices the agent
controls.** A lesson that reads well on canvas desktop can collapse into a broken guided
path if blocks are ordered or grouped carelessly. Design for beats, then let
auto-generation do the rest.

Guided flow also reveals blocks **one at a time**, with a Continue button between them.
This means each block needs to stand on its own visually - do not rely on the surrounding
blocks being visible for context; put the framing in the block's title, heading, or
first sentence.

**Answer-gate contract.** In guided flow, `quiz`, `cloze`, `sequence`, `essay`,
`custom_activity`, and `interaction` blocks HARD-BLOCK progression until the learner
completes them. Every gated block must be completable end-to-end (quiz with a valid
answer, cloze with bracketed answers + wordBank, >=2 real sequence items, essay with
prompt, custom_activity with a working submit step, interaction that is resolvable). A
gated block that cannot be completed silently traps the learner. Prefer non-gated
equivalents (text/callout/image/illustration/chart) for decorative blocks not meant to
be completed.

**Empty text blocks are silently filtered** in the player (`text | paragraph | h1-h6 |
quote | code` with no content). An empty block leaves no visible hole to catch during
editor preview, so do not ship placeholder-only text/heading blocks assuming they'll be
visible - they won't.

**Fork-friendly authoring (student notebooks).** Students can save any block into their
personal notebook. The notebook stores a **frozen snapshot** of the block at fork time,
so a student's saved copy stays valid even after the teacher edits the lesson. Author
every block to be MEANINGFUL WHEN DETACHED from the surrounding page: a callout carries
its own rule, a worked example carries problem + solution, a flashcard teaches without
the lesson context, an interaction includes title + observation prompt inside the
widget. This is the same rule as the guided-flow one-block-at-a-time reveal - both
flatten out contextual dependencies. Blocks that only make sense next to their
neighbours become unusable notebook items.

## How beats are generated

The app runs `generateMobileLearningBeats(page)`:

1. If `page.mobileBeatsOverride` is a non-empty array, it is used verbatim.
2. Else if `layout === "single"`: blocks are split on headings, and **every activity
   block closes the current beat**. So a beat is roughly:
   `[heading?] + explanation text/callout + one activity`.
3. Else (split layout): **each right-panel activity anchors one beat.** Left-panel blocks
   are attached to those beats either by heading section (when the left panel has more
   than one heading) or by even chunking (when it does not). Extra left groups become
   trailing beats.

Implication: the algorithm can only pair things that are ordered and signposted well.

## Beat-friendly authoring rules

Follow these so auto-generation produces a clean mobile path:

- **Signpost with headings.** A heading starts a new beat. Put one heading per teaching
  point so beats break where the meaning breaks.
- **Pair each activity with its explanation.** The left explanation that a right-panel
  activity practices should sit in the same heading section (or in matching order). Do
  not put all explanations first and all activities after.
- **Aim for rough 1:1.** When a split page has N right-panel activities, provide about N
  left-panel heading sections. This lets the generator map explanation -> activity
  cleanly instead of chunking blindly.
- **Order within a panel matters.** Setup before model before practice, top to bottom.
- **Keep supporting media next to what it explains** (image/callout beside its text).
- **One dominant activity per beat.** If a beat would contain several unrelated
  activities, split the teaching point across two headings.

## Mobile behavior by block type

`getMobileBehavior(block)` decides how each block behaves on a phone. Defaults:

| Behavior | Blocks | Meaning |
| --- | --- | --- |
| `full` (mobile-native) | text/headings/quote/callout/accordion, image, video, gallery, quiz, cloze, sequence, flashcard, checkpoint, `interaction` (graph/distribution/equation), responsive `artifact`, inline coding, small essay | Works fully on mobile |
| `viewer` | `canvas`, `mindmap`, `comparison`, `illustration`, pdf | Read/watch only on phone |
| `desktop_recommended` | `data-lab`, `embed`, immersive `coding`, complex `artifact`, essay > 600 words | Usable but better on desktop |

Override per block with `content.mobileBehavior` (`full | viewer | simplified |
desktop_recommended | desktop_required`).

**This intersects with the interactive-first rule.** For interactivity that must work on
mobile, prefer `interaction` widgets - they are `full`. Treat `canvas`, `illustration`,
`comparison`, and `mindmap` as watch-only on phones: still great, but do not make phone
lesson completion depend on manipulating them. If a block is genuinely desktop-only,
mark it `desktop_required` on purpose rather than shipping a cramped fake.

`artifact` blocks follow `content.mobileBehavior.mode`. Use `full` only when the artifact
is responsive and touch-friendly, `viewer` when it is read/watch only, and
`desktop_required` when the learning action truly cannot be completed on a phone.

## Setting beats explicitly (override)

Set an override only when clean auto-grouping is not achievable (e.g. two text blocks
must join one activity across a heading boundary):

```json
{
  "mobileBeatsOverride": [
    { "id": "beat-1", "label": "Introduce variables", "blockIds": ["text-a", "text-b", "quiz-a"] },
    { "id": "beat-2", "label": "Practice in code",    "blockIds": ["text-c", "coding-a"] }
  ]
}
```

- `label` is teacher-facing organization (auto-labeled from the first heading/text if
  omitted). `blockIds` reference block ids on the page, in beat order.
- Prefer fixing block order/headings over hand-authoring overrides. Overrides are the
  exception, not the default.

## Beat verification (add to preflight)

- Would this page auto-generate sensible beats? Mentally run the algorithm: does each
  right-panel activity land with the explanation it practices?
- Split pages: is the number of left heading sections roughly equal to the number of
  right activities?
- Does any beat mix several unrelated activities? If so, add a heading to split it.
- Are `viewer` / `desktop_recommended` blocks acceptable as-is on a phone, or should a
  mobile-native alternative (often an `interaction` widget) be used?
- If auto-grouping cannot be made clean, is `mobileBeatsOverride` set correctly?
