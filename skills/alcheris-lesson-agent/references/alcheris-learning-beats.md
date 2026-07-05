# Alcheris Learning Beats (Mobile Path)

Alcheris is a self-study product. Many learners open lessons on a phone. A desktop page
has two panels (left teaches, right acts); a phone has one column. Alcheris bridges the
two with **learning beats**.

A learning beat is a small teaching unit, one layer above blocks:

```text
setup / explanation  ->  model / example  ->  practice  ->  feedback / summary
```

On mobile, the lesson is rendered as a sequence of beats, not as two panels. The agent
that authors the lesson usually does not set beats by hand - the app auto-generates them.
But **beat quality is decided by authoring choices the agent controls.** A lesson that
reads well on desktop can collapse into a broken mobile path if blocks are ordered or
grouped carelessly. Design for beats, then let auto-generation do the rest.

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
| `full` (mobile-native) | text/headings/quote/callout/accordion, image, video, gallery, quiz, cloze, sequence, flashcard, checkpoint, `interaction` (graph/distribution/equation), inline coding, small essay | Works fully on mobile |
| `viewer` | `canvas`, `mindmap`, `comparison`, `illustration`, pdf | Read/watch only on phone |
| `desktop_recommended` | `data-lab`, `embed`, immersive `coding`, essay > 600 words | Usable but better on desktop |

Override per block with `content.mobileBehavior` (`full | viewer | simplified |
desktop_recommended | desktop_required`).

**This intersects with the interactive-first rule.** For interactivity that must work on
mobile, prefer `interaction` widgets - they are `full`. Treat `canvas`, `illustration`,
`comparison`, and `mindmap` as watch-only on phones: still great, but do not make phone
lesson completion depend on manipulating them. If a block is genuinely desktop-only,
mark it `desktop_required` on purpose rather than shipping a cramped fake.

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
