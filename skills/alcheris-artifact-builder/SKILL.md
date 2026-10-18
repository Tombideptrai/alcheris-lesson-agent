---
name: alcheris-artifact-builder
description: Build, fix, and ship Alcheris artifact blocks (sandboxed HTML/CSS/JS learning objects such as step-through animations, simulations, chart transformers, drag/drop or build-it activities) that fit the host frame on desktop, in the editor, and on phones. Use this whenever you create or edit an `artifact` block for an Alcheris lesson, turn an idea into an interactive or animated activity, or debug an artifact that is cut off, keeps growing taller, shows big empty gaps, looks tiny on mobile, clashes with the lesson theme, or won't save. Also use it when uploading or updating artifact code through the Alcheris MCP/connector. The lesson-agent skill decides *whether* a lesson needs an artifact; this skill covers *how* to build one that works.
---

# Alcheris artifact builder

An artifact is a small HTML/CSS/JS app that runs inside a sandboxed iframe in an Alcheris lesson. The host (the editor and the player) owns the frame, injects the theme, and listens through the `window.AlcherisArtifact` bridge. Most artifact bugs come from code that ignores how the host sizes that frame, so read the sizing section before writing CSS.

Use the bundled pieces instead of starting from a blank file:

| Path | What it is |
|---|---|
| `assets/starter/` | Working stepper template: `index.html`, `styles.css`, `engine.js`, `config.mjs`, `build.mjs`. Builds a valid definition out of the box, with tabs, an optional check step, dark-mode series colours and an opt-in `fitDrawing`. |
| `assets/examples/graph-skins/` | A real shipped example: one engine, two configs (table/bars/pies to line graph; table/pie to bar chart). |
| `scripts/validate_artifact.py` | Checks a `definition.json` against the host contract and the sizing rules before you upload. |
| `scripts/frame_check.html` | Test page that loads a built artifact in the real frame sizes (desktop, phone, adaptive) and reports whether it fits. |
| `references/frame-and-sizing.md` | How the host sizes frames, with the numbers. Read when layout misbehaves. |
| `references/contract.md` | Every definition field and validator rule. Read when a save is rejected. |
| `references/upload-and-verify.md` | Connector tool calls for adding, replacing, and verifying artifact blocks. |

## Workflow

1. **Confirm an artifact is the right block.** Native blocks (quiz, cloze, sequence, interaction graph, chart, illustration) are cheaper to build and maintain. Reach for an artifact when the learner has to *see something transform* or *do something* the native blocks can't express.

2. **Design one learner task per frame.** The frame never scrolls. Anything longer than one screen becomes explicit steps, tabs, or scenes with Back and Next. Write the step copy first (title, one-sentence description, Next button label), because it drives the layout.

3. **Scaffold from the starter.** Copy `assets/starter/` into the project (for example `artifacts/<slug>/`). Put content in `config.mjs` and drawing logic in `engine.js`, and keep `styles.css` shared. One engine with several configs is how you make a family of related artifacts without duplicating code (see the graph-skins example). Run `node build.mjs` to write `dist/<slug>/definition.json` plus loose files for local preview.

4. **Apply the sizing rules** (next section). They are the difference between an artifact that works and one that grows or gets cut off.

5. **Theme with host tokens and fixed data colours.** UI chrome uses the injected tokens (`--color-background`, `--color-foreground`, `--color-muted`, `--color-muted-foreground`, `--color-border`, `--color-primary`, `--color-primary-foreground`, `--color-success`, `--radius`, …) with sensible fallbacks, so it follows light/dark and teacher palettes. Data series do not: a series colour taken from `--color-primary` can collide with another series once a teacher's theme sets the primary to green or teal. Give series a fixed, distinct palette, plus a lighter set for dark backgrounds under `:root[data-alcheris-theme="dark"]` (the host sets this attribute). The starter's `styles.css` has both.

6. **Wire the bridge.** Call `window.AlcherisArtifact?.track(action, payload)` on meaningful steps, and `complete(payload)` when the learner finishes (with `completion.type: "manual"`). Use `submit(answer, { files })` only when a teacher should review the work. Guided flow blocks progress on artifacts, so an artifact that never calls `complete` or `submit` traps the learner. Use optional chaining so the file still runs standalone.

7. **Validate, then check the frame.**
   - `python scripts/validate_artifact.py dist/<slug>/definition.json` must pass.
   - Serve the project folder and open `scripts/frame_check.html?src=/dist/<slug>/index.html` (copy it next to `dist/` or serve a common parent). It reports, for each frame size, whether the tallest step fits and how much the drawing is scaled down. Aim for a scale of 0.8 or more on phones, and step through every tab.

8. **Upload and verify.** Follow `references/upload-and-verify.md`. In short: send the whole definition with `raw: true`, re-read the lesson, and compare the stored content with your built `definition.json`. When asked to work on a teacher's lesson, write to a copy unless they say otherwise.

## Sizing rules (why artifacts grow, gap, or get cut off)

The same artifact is framed two different ways:

- **Student player (inline):** a fixed frame of `width × preset ratio`, where `portrait` is 9:16 and `square` is 1:1. Content taller than this is clipped, because scrolling is disabled.
- **Editor, teacher preview, and full panel:** an *adaptive* frame. The bridge reports the document's content height and the host sets the frame to that height.

So:

- **Never size from the frame height.** No `height: 100vh`, `100%` height chains, or `min-height: 100vh` on the root. In adaptive mode, 100vh *is* the frame height you're reporting, so the frame locks at whatever size it first had (often far too tall, sometimes growing), leaving a big empty band around the content. This was the real bug in the first graph-skins build.
- **Size from the width only.** Let the root be content-height (`html, body` with no height, `.artifact` with no height). Give the drawing area a height derived from `100vw`, capped so that the whole artifact fits a 9:16 frame:
  ```css
  .stage {
    --ratio: 1.2222; /* drawing height ÷ width, e.g. 440/360 */
    height: min(calc((100vw - 2 * var(--pad)) * var(--ratio)), calc(100vw * 16 / 9 - 290px));
  }
  ```
  Here 290px is everything that isn't the drawing: tabs, header, footer, gaps, padding. Measure your own chrome and adjust. If the drawing's aspect ratio changes per step (for example a cropped `viewBox`), set `--ratio` from JS.
- **Compact the chrome on phones.** Phones get the 9:16 frame at about 320–360px wide, so every pixel of tabs and header comes out of the drawing. Under `@media (max-width: 420px)`, shrink tabs and buttons, drop reserved header heights, and use a smaller cap reserve (for example 215px). In graph-skins this took the chart from 63–72% scale to 80–89%.
- **Draw in SVG with a `viewBox`** and `preserveAspectRatio="xMidYMid meet"`, so the drawing scales as one piece. Keep SVG text at 10–12px at scale 1, so it stays readable at 0.8.
- **Let the drawing fill its stage (optional).** When the cap applies, the stage is shorter than the drawing's natural aspect ratio, and a fixed `viewBox` gets letterboxed. The starter's `fitDrawing: true` sets the `viewBox` height from the stage's real shape and redraws on resize, keeping the current step and replaying no animation. Lay the scene out from `VIEW.h`. With it on, don't set `--ratio` from JS, because the stage drives the drawing and not the other way round.
- **No internal scrolling.** `overflow: auto` or `overflow: scroll` anywhere in HTML or CSS is rejected by the validator. Split the content instead.

## Design notes that came from real feedback

- **Show one transformation in place.** When the source chart already sits on the target's axes (bars over time → line graph), mark the change directly on it: dots on the bar tips, then connect them. Drawing a second copy underneath was rejected as redundant.
- **Make every step change something visible**, and mirror it in the step copy. Reveal with motion (draw axes, pop dots, draw lines, fade or raise bars), and honour `prefers-reduced-motion`.
- **End with the learner doing something, not just watching.** Before the explanation step, add a check: "Where does the cyclist speed up?" or "Which bar is tallest?". The starter supports `check: { prompt, options, answer, hints, explain }` on any step. Next stays locked until the right answer or "Show me", wrong picks get their own hint, and answers are tracked. It draws as an overlay inside the stage, so it never changes the artifact's height. For questions that are better answered on the drawing itself (tap the dot, drag the point), make the SVG elements focusable buttons and reuse the same lock, hint and track pattern.
- **Write the Next label as the action** ("Draw the axes →", "Connect the dots →"). On the last step, offer the next tab or a replay, and call `complete` once every tab is done.
- **Keep the package small**: well under the 200 KB limit. The graph-skins files are about 22 KB each.

## Before you finish

- [ ] `validate_artifact.py` passes, with no errors and any warnings understood.
- [ ] `frame_check.html`: fits at 320, 343, and 620 wide in 9:16, the adaptive frame settles and doesn't grow, and the phone scale is about 0.8 or more on every step of every tab.
- [ ] Dark mode and a non-default primary colour both look right, and series colours stay distinct.
- [ ] `complete` (or `submit`) is reachable, so guided flow can't get stuck.
- [ ] The uploaded content is byte-identical to the built `definition.json`, checked by re-reading the lesson.
