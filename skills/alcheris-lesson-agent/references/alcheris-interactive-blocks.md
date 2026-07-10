# Alcheris Interactive Blocks

These are the "alive" blocks: they animate, reveal, or let the learner manipulate the
content directly. Most of them are **exploratory interactions**, not practice exercises:
they help the learner encounter, inspect, and understand an idea before answering
questions about it. Prefer them
over a static equivalent whenever the source material has movement, parameters, a
before/after state, or a process the learner should watch or drive.

Content shapes below are taken from the actual renderer/widget code. Author the
`content` object exactly as shown. Every value is plain JSON (no functions, no code).

Mobile note: each block has a default mobile behavior (see
`alcheris-learning-beats.md`). `interaction` widgets are mobile-native. `canvas`,
`mindmap`, `comparison`, and `illustration` become viewers on phones. Choose with the
mobile path in mind.

---

## interaction (the highest-leverage exploratory block)

One block type, four modes selected by `content.mode`. This is the block that most
often should replace a static chart image. It is usually part of explanation/exploration
and belongs with the teaching content, normally in the left panel on split pages.

### mode: "graph" - progressive trend reveal

Renders an animated line graph. A slider progressively reveals the data points, so the
learner uncovers the trend instead of seeing the finished chart. Set
`showFullGraph: true` to display the whole line at once (use on a reference/model page).

```json
{
  "mode": "graph",
  "graphTitle": "UK telephone calls by category, 1995-2002",
  "xAxisLabel": "Year",
  "yAxisLabel": "Billions of minutes",
  "showFullGraph": false,
  "graphData": [
    { "id": "p1", "label": "1995", "value": 70 },
    { "id": "p2", "label": "1999", "value": 90, "annotation": "Peak" },
    { "id": "p3", "label": "2002", "value": 70 }
  ]
}
```

- `graphData[]`: each point needs `id`, `label` (x-axis tick), `value` (y). `annotation`
  is optional and draws a small callout on the point.
- Multiple lines: instead of `graphData`, provide `series: [{ label, color?, points:[{label,value,annotation?}] }]`
  (one entry per line). The widget draws every line with a legend and a shared slider reveal.
  Use this when a chart has several categories over the same time axis.
- Use over a static `image` chart whenever the data changes across time and the learner
  should notice the movement. The slider reveal is the teaching moment.
- Do NOT put the answer in `annotation` on a point that appears before a quiz about it.

### mode: "distribution" - live bell curve

Two sliders (mean, standard deviation) reshape a normal distribution in real time. Set
`allowStudentInteraction: false` to lock the sliders and show a fixed teacher-set curve.

```json
{
  "mode": "distribution",
  "statTitle": "How spread changes the curve",
  "statInstruction": "Drag the sliders to see how mean and standard deviation reshape the data.",
  "statMean": 50,
  "statStdDev": 10,
  "allowStudentInteraction": true
}
```

- Use when teaching spread, averages, variance, normal distributions, or "what happens
  if we change this parameter" - instead of a static curve image plus prose.

### mode: "equation" - function grapher / puzzle

Graphs `f(x)` from an editable expression with variable sliders. `gameMode: true` plus
`targets` turns it into a "make the curve pass through these points" puzzle.

```json
{
  "mode": "equation",
  "mathExpression": "a * x^2 + b",
  "mathA": 1,
  "mathB": 0,
  "mathC": 0,
  "mathXMin": -10, "mathXMax": 10, "mathYMin": -10, "mathYMax": 10,
  "mathAllowUserEdit": true,
  "showLinkedTable": true,
  "gameMode": false,
  "targets": [ { "x": -5, "y": 5 }, { "x": 0, "y": 0 }, { "x": 5, "y": 5 } ]
}
```

- `mathAllowUserEdit: false` locks the expression (learner only moves sliders).
- `showLinkedTable: true` shows a synced numeric X/Y table beside the graph.
- Use for functions, transformations, parameters, and "match the curve" challenges.

---

## illustration - animated, staged visual explanation

A keyframed scene player. Multiple scenes auto-play and auto-advance; each scene has
layers (shapes, text, images, svg) animated by keyframes. Use when a process,
transformation, or relationship is best *shown in motion* - not as a bullet list.

```json
{
  "version": 1,
  "stage": { "width": 1280, "height": 720, "backgroundColor": "#f8fafc", "fit": "contain" },
  "scenes": [
    {
      "id": "scene-1",
      "title": "Bars become a line",
      "durationMs": 4000,
      "layers": [
        { "id": "bar1", "type": "shape", "shape": "rect", "x": 200, "y": 400, "width": 80, "height": 160, "fill": "#dbeafe", "stroke": "#2563eb" },
        { "id": "label1", "type": "text", "x": 200, "y": 300, "width": 300, "height": 80, "text": "Each bar is one point", "color": "#0f172a", "fontSize": 42 }
      ],
      "keyframes": {
        "bar1": [
          { "timeMs": 0, "easing": "easeOut", "props": { "opacity": 0, "scaleY": 0.5 } },
          { "timeMs": 900, "easing": "easeOut", "props": { "opacity": 1, "scaleY": 1 } }
        ],
        "label1": [
          { "timeMs": 500, "easing": "easeOut", "props": { "opacity": 0, "y": 340 } },
          { "timeMs": 1400, "easing": "easeOut", "props": { "opacity": 1, "y": 300 } }
        ]
      }
    }
  ]
}
```

- Layer `type`: `shape` (needs `shape`, e.g. `rect`), `text` (needs `text`), `image`/`svg`
  (need `src`). Common props: `x, y, width, height, opacity, rotation, scaleX, scaleY,
  fill, stroke, color, fontSize, borderRadius`.
- Keyframes are keyed by layer id. Each keyframe: `timeMs`, `easing`
  (`linear|easeIn|easeOut|easeInOut`), and `props` (the target values at that time).
- Keep on-screen text short; this is a visual, not a paragraph. Verify no overlap.
- Mobile default is `viewer` - fine for watching, not for precise editing.

---

## comparison - before/after

Three types via `content.compareType`. Image = draggable slider; text = word-level
diff; code = line-level diff. Use instead of stacking two images/blocks when the
*change* is the lesson.

```json
{ "compareType": "image", "height": 450, "beforeImage": "<url>", "afterImage": "<url>" }
```
```json
{ "compareType": "text", "height": 450, "beforeText": "The graph go up.", "afterText": "The graph rose steadily." }
```
```json
{ "compareType": "code", "height": 450, "beforeCode": "for(i)...", "afterCode": "for (let i ...)" }
```

- `image` also accepts `beforeAnnotations` / `afterAnnotations` (`{ markers:[], drawings:[] }`).
- Great for writing upgrades (weak -> strong sentence), refactors, and edited visuals.

---

## canvas - replayable drawing

Plays back drawn `paths` like a hand drawing live. Use to build a diagram step by step,
or as a student sketch surface. Mobile default is `viewer`.

```json
{
  "height": 400,
  "backgroundColor": "#ffffff",
  "backgroundPattern": "plain",
  "paths": [],
  "images": [],
  "speed": 1,
  "autoplay": false,
  "showReplayButton": true,
  "instantReplay": false
}
```

- `paths` hold the stroke data (authored in the visual editor). `autoplay: true` draws on
  view; `showReplayButton: true` lets the learner replay the build.

---

## mindmap - node/relationship map

```json
{
  "nodes": [
    { "id": "root", "x": 300, "y": 150, "label": "Central idea", "type": "root", "color": "#3b82f6" },
    { "id": "n1", "x": 480, "y": 90, "label": "Branch A", "color": "#22c55e" }
  ]
}
```

- Use for concept maps, brainstorms, and relationship structures. Mobile default `viewer`.

---

## Interactive-first decision rule

When the source material has any of these signals, reach for the interactive block, not
the static equivalent:

| Source signal | Use | Instead of |
| --- | --- | --- |
| Data changes over time | `interaction` mode `graph` (slider reveal) | static chart `image` |
| A parameter/spread/average concept | `interaction` mode `distribution` | static curve image + prose |
| A function or "what if we change X" | `interaction` mode `equation` | static formula + example |
| A process/transformation to watch | `illustration` (staged scenes) | bullet list of steps |
| A before/after change is the point | `comparison` | two stacked images/blocks |
| A diagram built step by step | `canvas` (replay) | one finished diagram image |
| Concepts and their relationships | `mindmap` | a flat list |

Engagement patterns (why these blocks exist):

- Reveal before explain: let the learner uncover the trend/curve first, then teach it.
- Manipulate before tell: let them move the slider and form a hypothesis before the rule.
- Watch before summarize: play the transformation, then state the takeaway.

Do not overuse: one interactive block per teaching point is enough. The goal is active
thinking, not decoration.
