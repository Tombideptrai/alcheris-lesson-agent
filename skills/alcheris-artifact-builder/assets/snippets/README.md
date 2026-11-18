# Snippets from the CFA rebuild

Drop-in helpers for motion-first artifacts. They pair with `index.html` here (a header,
a `#board` container, and a footer with Back / dots / Next). The starter's stepper uses a
different shell, so use these when you write your own engine.

| File | What it gives you |
|---|---|
| `motion.js` | `tween()` / `wait()` that freeze when the step changes, `EASE`, `countTo()`, `shake()`, `usd()`, `draggable()` (window-tracked pointer drag, safe on phones), and `scenes(C, runners)`: header, dots, Back/Next, `api.say()`, `api.finish()`, completion and auto-advance. It also sets `window.__alcScene(k)`, which `scripts/shoot_scenes.py` uses to reach every scene. Expects `const C = CONFIG` before it. |
| `auto.js` | `autoNext(go, text)` and `cancelAuto()`: after a fresh success, wait about 1.8 to 5 s (by word count) while the Next button fills, then go on. Tapping Next skips. |
| `report.js` | Reports the artifact's height to the host via `AlcherisArtifact.resize()` on every DOM change, plus retries, and re-reports when the frame's width changes (the guided player can mount it at 0px wide). Include it in every artifact. |
| `chart-text.css` | A halo for labels that sit on lines and bars, and bigger chart text on phones. Rename the classes to yours. |

Build order inside `script.js`: `const CONFIG = {...}` → `const C = CONFIG` → `motion.js` (optional) → `auto.js` → your engine → `report.js`.

A runner for `scenes()` looks like:

```js
scenes(C, [
  (api, cfg) => {
    const svg = /* build the drawing */;
    api.start = () => {               // runs after the DOM is in place
      api.say(cfg.say);
      draggable(handle, svg, { onMove: (p) => { /* follow the finger */ }, onUp: () => { api.say(cfg.done, "good"); api.finish(); } });
    };
    return [svg];
  },
]);
```
