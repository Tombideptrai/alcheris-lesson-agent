# Example: A Trend-Graph Page, Done Right

This is a before/after that shows the single most common miss: an agent drops a **static
chart image** where a live **`interaction` graph** would let the learner uncover the
trend. Same lesson content, very different experience.

## The miss (static, "boring")

```text
Page: "Practice Writing an Overall"  (layout: split)
LEFT
  - h2: "The overall gives the big story"
  - image: <screenshot of the finished line chart>   <-- static; trend already visible
  - text: bullet list of tips
RIGHT (rightPanelMode: essay)
  - essay: "Write only the overall in 35-60 words."
```

The learner reads a finished chart and types. Nothing to explore. The chart also spoils
the movement the overall is supposed to describe.

## Done right (interactive + beat-friendly)

Replace the static image with an `interaction` graph in slider-reveal mode, so the
learner drags to uncover the trend and forms the "big story" themselves before writing.

```json
{
  "title": "Practice Writing an Overall",
  "layout": "split",
  "rightPanelMode": "essay",
  "leftPanel": [
    { "type": "h2", "content": { "text": "The overall gives the big story" } },
    {
      "type": "interaction",
      "content": {
        "mode": "graph",
        "graphTitle": "UK telephone calls by category, 1995-2002",
        "xAxisLabel": "Year",
        "yAxisLabel": "Billions of minutes",
        "showFullGraph": false,
        "graphData": [
          { "id": "p1", "label": "1995", "value": 72 },
          { "id": "p2", "label": "1999", "value": 90 },
          { "id": "p3", "label": "2002", "value": 70 }
        ]
      }
    },
    {
      "type": "callout",
      "content": { "text": "Drag the slider to watch the movement. The overall names the biggest changes - not every number." }
    }
  ],
  "rightPanel": [
    {
      "type": "essay",
      "content": {
        "prompt": "Write only the overall in 35-60 words. Name the biggest movements you just watched, not exact figures.",
        "minWords": 35,
        "maxWords": 60
      }
    }
  ]
}
```

What changed and why it matters:

- **Reveal before explain.** `showFullGraph: false` means the slider uncovers the trend;
  the learner notices the rise-then-fall before being told about it.
- **The interactive graph is the stimulus.** No separate static image is needed. If the
  data moves over time, the live graph is preferred.
- **No spoiler.** The finished shape is not sitting on the page before the writing task.

## Why the mobile path is fine here

- `interaction` is mobile-native (`full`), so the slider reveal works on a phone.
- The page has one right-panel activity (the essay) anchored by one left heading section,
  so beat generation produces a single clean beat:
  `[h2 + interaction graph + callout] -> essay`. Explanation and action stay together on
  mobile. No `mobileBeatsOverride` needed.

## The general rule

When source material has movement, parameters, a before/after state, or a process, author
the interactive block (`references/alcheris-interactive-blocks.md`) instead of the static
equivalent, and order blocks so each activity pairs with its explanation
(`references/alcheris-learning-beats.md`).
