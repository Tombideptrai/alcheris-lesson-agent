# How Alcheris frames an artifact

Source of truth: `frontend/src/features/block/artifact/ArtifactBlock.jsx` and `artifactContract.js` in the lesson-maker repo. If behaviour here disagrees with the code, trust the code and update this file.

## Two framing modes

`ArtifactBlock` renders the iframe with `adaptiveHeight = isFullPanelMode || isEditable || suppressTracking`.

| Where | Mode | Frame size |
|---|---|---|
| Student player, inline in a page or beat | fixed | `width: 100%`, `aspect-ratio: <preset>` (portrait 9/16, square 1) |
| Editor canvas (`isEditable`) | adaptive | height = reported content height (max 8192px) |
| Teacher preview (`?preview=1`, so `suppressTracking`) | adaptive | same |
| Full panel (`rightPanelMode: artifact`) | adaptive, inside a stage fitted to the preset ratio | same |

In adaptive mode the injected bridge reports
`max(body.offsetHeight, bottom of body's last child + body padding-bottom)` through a `ResizeObserver` on `<html>` and `<body>`, and the host sets the iframe height to that value.

The host also injects this CSS, which overrides any height you give `html` or `body`:

```css
html, body { width: 100%; height: auto !important; min-height: 0 !important; margin: 0; overflow: hidden !important; }
```

## Why `100vh` breaks

In adaptive mode, `100vh` equals the current iframe height. A root sized `height: 100vh` reports exactly the frame height it was given, so the loop never shrinks. The frame stays at its first size. That first size is usually the preset-ratio frame from before the first report, computed at whatever width the panel had then (for example a wide single-column page before it went split). The visible result is a frame two or three times taller than the content, with the drawing centred in a huge empty band. If anything adds a few pixels on each report, it grows instead.

Content sized from the width has a fixed natural height for a given width, so both modes agree.

## The width-only layout

```css
:root { --pad: clamp(10px, 3vw, 18px); }
html, body { margin: 0; overflow: hidden; }          /* no height */
.artifact { display: grid; grid-template-rows: auto auto auto auto; gap: 10px; padding: var(--pad); } /* no height */
.stage {
  --ratio: 1.2222;                                    /* drawing h/w */
  height: min(calc((100vw - 2 * var(--pad)) * var(--ratio)), calc(100vw * 16 / 9 - 290px));
  min-height: 220px;
}
#stage { display: block; width: 100%; height: 100%; } /* the SVG */
```

- The first term is the drawing's natural height at full width.
- The second term caps the total so that header, tabs, footer, and the drawing fit inside a 9:16 frame of the same width. Set the reserve (290px here) to your measured chrome height plus a small margin.
- In a wide desktop column the natural term usually wins, and the frame has spare room at the bottom. That's fine, because the content is top-aligned.
- With a `square` preset, swap `16 / 9` for `1`.

## Phones

The mobile path (`mobileLearningBeats.js`) renders artifacts with `mobileBehavior.mode: "full"` inline, so it uses the fixed frame at the phone's content width:

| Device | Frame (9:16) |
|---|---|
| Small Android | 320 × 569 |
| iPhone 14/15 (390 screen, about 343 content) | 343 × 610 |
| Large phone (430 screen, about 383 content) | 383 × 681 |

Chrome that is fine on desktop (36px tabs, a 92px reserved header, 42px buttons) eats a third of a phone frame. Tighten it under `@media (max-width: 420px)` and lower the cap reserve to match. Graph-skins went from 0.63–0.72 to 0.80–0.89 drawing scale this way.

`mobileBehavior.mode` options: `full`, `viewer`, `simplified` (treated as `viewer`), `desktop_recommended`, `desktop_required`. Use `desktop_*` only when the activity truly cannot work by touch at phone width.

## Measuring

`scripts/frame_check.html` loads your built artifact in fixed frames (320×569, 343×610, 620×1102) and in an adaptive frame that copies the host loop. For each one it steps through every tab and step and reports:

- `tallest`: the largest content height across steps,
- `fits`: `tallest <= frame height` (fixed frames only),
- `minScale`: the smallest SVG scale factor (drawing size ÷ `viewBox` size),
- for the adaptive frame, whether the height settled (it should be identical across samples).

It expects the starter's DOM conventions: `.artifact`, `.tab`, `#next`, and `svg#stage`.
